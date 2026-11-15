#!/usr/bin/env python3
"""DeepSeek visual reviewer for MPL ID S18 screenshots.

This tool is the second-stage visual reviewer. It sends the original screenshot
bytes to a DeepSeek vision model (direct `deepseek-flash` or a DeepSeek model
hosted by the local OpenCode session API), records the exact image/sidecar
hashes, and writes a review ledger. It never marks a frame reviewed unless the
API returned a parsed observation for that image. It never promotes a game
boundary; boundary findings are recorded for a later, explicit promotion step.

Usage:
    python tools/deepseek_visual_review.py smoke --backend direct [--opencode-credential]
    python tools/deepseek_visual_review.py smoke --backend opencode-go-session
    python tools/deepseek_visual_review.py run --backend opencode-go-session \
        --plan analysis/evidence/visual-review-plan.json \
        --smoke analysis/evidence/deepseek-vision-smoke-opencode-go.json \
        --out analysis/evidence/deepseek-visual-reviews.json [--resume]

Backends:
    direct                 Direct https://api.deepseek.com chat completions (deepseek-flash).
    opencode-session       Local OpenCode session API, deepseek-v4.1-flash-free.
    opencode-go-session    Local OpenCode session API, opencode-go/deepseek-v4.1-flash.

API key resolution (direct backend):
    1. DEEPSEEK_API_KEY environment variable (preferred; used by CI).
    2. --opencode-credential reads the active DeepSeek key from the local
       OpenCode credential service. The key is never printed or written to disk.
The session backends use the local OpenCode service credential and the active
DeepSeek model configured there; no key is written to disk.

The review contract is in docs/goals/active/mpl-s18-visual-proof-deepseek-handoff.md.
No human visual-review queue is used.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_PLAN = REPO / "analysis" / "evidence" / "visual-review-plan.json"
DEFAULT_OUT = REPO / "analysis" / "evidence" / "deepseek-visual-reviews.json"
DEFAULT_SMOKE = REPO / "analysis" / "evidence" / "deepseek-vision-smoke.json"
RAW_DIR = REPO / "analysis" / "cache" / "visual-reviews"
API_BASE = "https://api.deepseek.com"
MODEL = "deepseek-flash"
REVIEWER = "deepseek"
PROMPT_VERSION = "deepseek-visual-review-v1"

BACKENDS = {
    "direct": {
        "mode": "direct-chat-completions",
        "provider": "deepseek",
        "model": "deepseek-flash",
        "api_base": "https://api.deepseek.com",
        "transport": "https+json",
    },
    "opencode-session": {
        "mode": "opencode-session",
        "provider": "opencode",
        "model": "deepseek-v4.1-flash-free",
        "api_base": "http://127.0.0.1:28894",
        "transport": "local-opencode-session-api",
    },
    "opencode-go-session": {
        "mode": "opencode-session",
        "provider": "opencode-go",
        "model": "deepseek-v4.1-flash",
        "variant": "max",
        "api_base": "http://127.0.0.1:28894",
        "transport": "local-opencode-session-api",
    },
}
ACTIVE_BACKEND = dict(BACKENDS["direct"])

DISPOSITIONS = {"used", "rejected", "context-only", "inconclusive"}
CONFIDENCES = {"high", "med", "low"}
NEGATIVE_ANSWERS = {"no", "false", "not visible", "unclear", "none", "n/a", "unknown",
                    "not legible", "illegible", "cannot tell", "not shown"}

ALIASES = {
    "EVOS": ["EVOS"],
    "RRQ": ["RRQ", "RRQ HOSHI"],
    "NAVI": ["NAVI"],
    "AE": ["AE", "ALTER EGO"],
    "ONIC": ["ONIC"],
    "TLID": ["TLID", "TEAM LIQUID ID", "TEAM LIQUID", "LIQUID ID"],
    "BTR": ["BTR", "BIGETRON", "VITALITY"],
    "GEEK": ["GEEK", "GEEKFAM"],
    "DEWA": ["DEWA", "DEWA UNITED"],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def sha256_text_lf(path: Path) -> str:
    """Hash a committed JSON/text artifact with LF endings so every checkout agrees."""
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


def atomic_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def repo_path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else REPO / p


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO)).replace("\\", "/")
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# API key + transport
# ---------------------------------------------------------------------------

def load_api_key(opencode_credential: bool = False, opencode_base: str = "http://127.0.0.1:28894") -> tuple[str, str]:
    if ACTIVE_BACKEND["mode"] == "opencode-session":
        return "", "opencode-session"
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key, "DEEPSEEK_API_KEY"
    if not opencode_credential:
        raise SystemExit(
            "No DeepSeek API key. Set DEEPSEEK_API_KEY, or pass --opencode-credential "
            "to read the active key from the local OpenCode credential service."
        )
    service = Path(os.path.expanduser("~")) / ".config" / "opencode" / "service.json"
    if not service.exists():
        raise SystemExit(f"OpenCode service config not found: {service}")
    password = json.loads(service.read_text(encoding="utf-8"))["password"]
    token = base64.b64encode(f"opencode:{password}".encode()).decode()
    req = urllib.request.Request(
        f"{opencode_base.rstrip('/')}/api/credential",
        headers={"Authorization": f"Basic {token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.load(resp)
    for row in data.get("data", []):
        if row.get("integrationID") == "deepseek" and row.get("active"):
            value = row.get("value") or {}
            if value.get("type") == "key" and value.get("key"):
                return value["key"].strip(), "opencode-credential-service"
    raise SystemExit("No active DeepSeek key found in the OpenCode credential service.")


# ---------------------------------------------------------------------------
# Local OpenCode session transport (DeepSeek model hosted by OpenCode)
# ---------------------------------------------------------------------------

def opencode_headers() -> dict:
    service = Path(os.path.expanduser("~")) / ".config" / "opencode" / "service.json"
    if not service.exists():
        raise SystemExit(f"OpenCode service config not found: {service}")
    password = json.loads(service.read_text(encoding="utf-8"))["password"]
    token = base64.b64encode(f"opencode:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def opencode_call(method: str, path: str, body: dict | None = None, timeout: int = 60) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(ACTIVE_BACKEND["api_base"].rstrip("/") + path, data=data,
                                 headers=opencode_headers(), method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        if not raw:
            return {}
        return json.loads(raw)


def opencode_wait(session_id: str, user_message_id: str, timeout: int = 300) -> dict:
    deadline = time.time() + timeout
    assistant = None
    seen = False
    while time.time() < deadline:
        time.sleep(1.0)
        data = opencode_call("GET", f"/api/session/{session_id}/message?order=asc&limit=100")
        messages = data.get("data", [])
        for msg in messages:
            if msg.get("id") == user_message_id:
                seen = True
            if msg.get("type") == "assistant" and seen:
                if msg.get("time", {}).get("completed"):
                    assistant = msg
            if msg.get("type") == "idle" and seen:
                outcome = msg.get("outcome")
                if assistant is not None:
                    return assistant
                if outcome in ("failed", "cancelled", "error"):
                    raise BadResponse(f"opencode session ended with outcome={outcome}")
        if assistant is not None and assistant.get("content"):
            # The assistant message is complete; the idle marker may lag slightly.
            return assistant
    raise BadResponse(f"opencode session timed out after {timeout}s (session={session_id})")


def opencode_session_request(images: list[bytes], prompt: str) -> dict:
    """Run one stateless visual-review turn through the local OpenCode session API."""
    model_ref = {"id": ACTIVE_BACKEND["model"], "providerID": ACTIVE_BACKEND["provider"]}
    if ACTIVE_BACKEND.get("variant"):
        model_ref["variant"] = ACTIVE_BACKEND["variant"]
    session = opencode_call("POST", "/api/session", {
        "title": "DeepSeek visual review " + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "agent": "explore",
        "model": model_ref,
    })
    session_id = session["data"]["id"]
    input_dir = RAW_DIR / "session-inputs" / session_id
    input_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for index, image in enumerate(images):
        p = input_dir / f"image-{index}.png"
        p.write_bytes(image)
        uri = p.resolve().as_uri()
        files.append({
            "uri": uri,
            "source": {"type": "uri", "uri": uri},
            "name": p.name,
            "description": f"visual evidence frame {index + 1}",
        })
    user = opencode_call("POST", f"/api/session/{session_id}/prompt", {
        "text": prompt + "\n\nDo not use any tools. The images are attached; answer from the attached pixels only.",
        "files": files,
        "resume": True,
    })
    user_id = user["data"]["id"]
    message = opencode_wait(session_id, user_id)
    content = "\n".join(
        str(part.get("text", "")) for part in message.get("content", [])
        if part.get("type") == "text"
    ).strip()
    if not content:
        raise EmptyResponse(f"opencode session returned no text (session={session_id})")
    tokens = message.get("tokens") or {}
    usage = {
        "prompt_tokens": tokens.get("input"),
        "completion_tokens": tokens.get("output"),
        "total_tokens": (tokens.get("input") or 0) + (tokens.get("output") or 0),
        "reasoning_tokens": tokens.get("reasoning"),
        "cache_read": (tokens.get("cache") or {}).get("read"),
        "cache_write": (tokens.get("cache") or {}).get("write"),
    }
    created = int((message.get("time", {}).get("created") or 0) / 1000)
    return {
        "id": message.get("id"),
        "model": (message.get("model") or {}).get("id", ACTIVE_BACKEND["model"]),
        "created": created,
        "choices": [{
            "message": {"role": "assistant", "content": content},
            "finish_reason": message.get("finish") or message.get("rawFinish"),
        }],
        "usage": usage,
        "_session_id": session_id,
        "_provider": (message.get("model") or {}).get("providerID", ACTIVE_BACKEND["provider"]),
        "_agent": message.get("agent"),
        "_cost": message.get("cost"),
        "_raw_message": {
            "id": message.get("id"),
            "time": message.get("time"),
            "model": message.get("model"),
            "finish": message.get("finish"),
            "tokens": message.get("tokens"),
            "content": message.get("content"),
        },
    }


def api_request(key: str, images: list[bytes], prompt: str, *, max_tokens: int,
                timeout: int = 300) -> dict:
    if ACTIVE_BACKEND["mode"] == "opencode-session":
        return opencode_session_request(images, prompt)
    content = [{"type": "text", "text": prompt}]
    for image in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": "data:image/png;base64," + base64.b64encode(image).decode()},
        })
    body = {
        "model": MODEL,
        "temperature": 0,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": content}],
    }
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def parse_json_content(content: str):
    text = (content or "").strip()
    if not text:
        raise ValueError("empty response content")
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    starts = [i for i in (text.find("["), text.find("{")) if i >= 0]
    if not starts:
        raise ValueError(f"no JSON in response: {text[:200]!r}")
    start = min(starts)
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text[start:])
    return obj


class EmptyResponse(RuntimeError):
    pass


class BadResponse(RuntimeError):
    pass


def call_with_retry(key: str, images: list[bytes], prompt: str, *, max_tokens: int,
                    call_id: str, group_id: str) -> tuple[dict, dict]:
    """Return (parsed_json, call_record). Retry empty/over-budget responses and transient errors."""
    attempts = []
    token_budget = max_tokens
    for attempt in range(1, 5):
        started = time.time()
        try:
            raw = api_request(key, images, prompt, max_tokens=token_budget)
            choice = raw["choices"][0]
            content = choice["message"].get("content") or ""
            finish = choice.get("finish_reason")
            if not content.strip():
                raise EmptyResponse(f"empty content (finish={finish}, max_tokens={token_budget})")
            parsed = parse_json_content(content)
            record = {
                "call_id": call_id,
                "group_id": group_id,
                "provider": raw.get("_provider", ACTIVE_BACKEND["provider"]),
                "model": raw.get("model", ACTIVE_BACKEND["model"]),
                "transport": ACTIVE_BACKEND["mode"],
                "session_id": raw.get("_session_id"),
                "agent": raw.get("_agent"),
                "cost": raw.get("_cost"),
                "request_id": raw.get("id"),
                "created": raw.get("created"),
                "usage": raw.get("usage", {}),
                "finish_reason": finish,
                "attempt": attempt,
                "max_tokens": token_budget,
                "duration_ms": int((time.time() - started) * 1000),
                "image_sha256": [sha256_bytes(i) for i in images],
                "prompt_sha256": sha256_bytes(prompt.encode()),
                "raw_content": content,
            }
            if raw.get("_raw_message"):
                record["raw_message"] = raw["_raw_message"]
            return parsed, record
        except (EmptyResponse, BadResponse, ValueError) as exc:
            attempts.append({"attempt": attempt, "max_tokens": token_budget, "error": str(exc)})
            token_budget = min(16000, int(token_budget * 1.5))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            attempts.append({"attempt": attempt, "max_tokens": token_budget,
                             "error": f"HTTP {exc.code}: {detail}"})
            if exc.code not in (429, 500, 502, 503, 504):
                break
            time.sleep(min(20, 2 ** attempt))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            attempts.append({"attempt": attempt, "max_tokens": token_budget, "error": str(exc)})
            time.sleep(min(20, 2 ** attempt))
    raise BadResponse(json.dumps(attempts, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Prompt + frame preparation
# ---------------------------------------------------------------------------

def build_prompt(group: dict, n_images: int) -> str:
    if n_images == 1:
        shape = "a JSON object"
        index_note = ""
    else:
        shape = f"a JSON array of exactly {n_images} objects, one per image in the order supplied"
        index_note = " Each object must include image_index (0-based) and no other ordering key."
    keys = (
        "observation (string), visible_text (array of exact visible strings), answers (object with short "
        "descriptive keys), model_disposition (used|rejected|context-only|inconclusive), "
        "confidence (high|med|low), limitations (string)"
    )
    return (
        "You are a strict visual evidence reviewer. Inspect only the pixels in the supplied image(s). "
        "Do not use outside knowledge. Do not infer events from hero positions, score, team reputation, "
        "or metadata. If text is not legible, write [illegible]; do not guess. Answer concisely; do not "
        "deliberate or restate the task.\n\n"
        f"Claim under review: {group['claim']}\n\n"
        f"Task: {group['question']}\n\n"
        f"Return ONLY {shape} with keys: {keys}.{index_note} "
        "For model_disposition: used only if the pixels themselves establish the claim; rejected if they "
        "contradict the claim; context-only if the frame is related but insufficient; inconclusive if "
        "ambiguous. The harness will independently verify your answers against the claim. Do not wrap the "
        "JSON in markdown fences."
    )


def prepare_frame(frame: dict) -> tuple[Path, bytes, dict, dict]:
    path = repo_path(frame["path"])
    if not path.exists():
        raise SystemExit(f"frame missing: {path}")
    data = path.read_bytes()
    side_path = repo_path(frame.get("sidecar_path") or str(path.with_suffix(".json")))
    side = load_json(side_path) if side_path.exists() else {}
    meta = {
        "frame_id": frame["frame_id"],
        "historical_frame_id": frame.get("historical_frame_id"),
        "path": rel(path),
        "sidecar_path": rel(side_path),
        "screenshot_sha256": sha256_bytes(data),
        "sidecar_sha256": sha256_file(side_path) if side_path.exists() else None,
        "source_id": side.get("source_id"),
        "video_id": side.get("video_id"),
        "requested_seconds": side.get("requested_seconds"),
        "actual_seconds": side.get("actual_seconds"),
        "timestamp_link": side.get("timestamp_link"),
        "capture_status": side.get("status", frame.get("capture_status", "unknown")),
        "sidecar_output_sha256": side.get("output_sha256"),
        "sidecar_output_bytes": side.get("output_bytes"),
        "video_width": side.get("video_width", side.get("width")),
        "video_height": side.get("video_height", side.get("height")),
        "derived_from_path": side.get("derived_from_path"),
        "derived_from_sha256": side.get("derived_from_sha256"),
        "crop_box": side.get("crop_box"),
        "note": frame.get("note"),
    }
    if meta["sidecar_output_sha256"]:
        meta["sidecar_hash_matches"] = meta["sidecar_output_sha256"] == meta["screenshot_sha256"]
    else:
        meta["sidecar_hash_matches"] = None
    return path, data, side, meta


def normalize_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def answer_value(output: dict, key: str) -> str:
    answers = output.get("answers") or {}
    if key in answers:
        return str(answers[key])
    return ""


def searchable(output: dict) -> str:
    parts = [str(output.get("observation", ""))]
    parts.extend(normalize_list(output.get("visible_text")))
    for value in (output.get("answers") or {}).values():
        parts.append(str(value))
    return " ".join(parts).lower()


def is_negative_answer(value: str) -> bool:
    v = str(value or "").strip().lower()
    if not v:
        return False
    return any(
        v == neg or v.startswith(neg + " ") or v.startswith(neg + ",") or
        v.startswith(neg + ";") or v.startswith(neg + ":")
        for neg in NEGATIVE_ANSWERS
    )


def req_satisfied(requirement: dict, output: dict) -> bool:
    alternatives = [a.lower() for a in requirement.get("any", [])]
    answers = output.get("answers") or {}
    # Explicit answer-key aliases are used for yes/no/visibility questions. A
    # negative answer (e.g. "No; 'HAS SLAIN' is not visible") must fail even if
    # the quoted evidence text contains the searched token.
    for key in requirement.get("answer_keys", []):
        if key not in answers:
            continue
        value = str(answers[key])
        if is_negative_answer(value):
            return False
        if any(alt in value.lower() for alt in alternatives):
            return True
        if re.search(r"\b(yes|visible|present|legible|shown|confirmed)\b", value, re.I):
            return True
    # Numeric/text tokens are checked against the model's exact visible-text list.
    visible = " ".join(normalize_list(output.get("visible_text"))).lower()
    if any(alt in visible for alt in alternatives):
        return True
    return False


def required_answers_satisfied(rule: dict, output: dict) -> tuple[bool, list[str]]:
    missing = []
    answers = output.get("answers") or {}
    for key, alternatives in (rule.get("required_answers") or {}).items():
        value = str(answers.get(key, "")).lower()
        if not value or is_negative_answer(value) or not any(str(alt).lower() in value for alt in alternatives):
            missing.append(f"{key}={answers.get(key)!r}")
    return not missing, missing


def evaluate_frame(group: dict, output: dict, meta: dict) -> dict:
    rule = group.get("rule") or {"type": "any"}
    checks = []
    model_disp = str(output.get("model_disposition") or output.get("disposition") or "inconclusive").lower()
    if model_disp not in DISPOSITIONS:
        model_disp = "inconclusive"
    confidence = str(output.get("confidence") or "low").lower()
    if confidence not in CONFIDENCES:
        confidence = "low"

    forced = group.get("force_disposition")
    if forced:
        disposition = forced
        basis = f"forced: {group.get('force_reason') or 'policy'}"
        checks.append({"name": "force", "passed": False, "reason": basis})
    elif rule.get("type") == "required_text":
        for requirement in rule.get("required", []):
            passed = req_satisfied(requirement, output)
            checks.append({"name": requirement.get("name"), "passed": passed})
        required_ok = all(c["passed"] for c in checks)
        answers_ok, missing_answers = required_answers_satisfied(rule, output)
        if not answers_ok:
            checks.append({"name": "required_answers", "passed": False,
                           "missing": missing_answers})
        if required_ok and answers_ok:
            disposition = "used"
            basis = "all required visible values/answers matched"
        elif any(c["passed"] for c in checks):
            disposition = "context-only"
            missing = [c["name"] for c in checks if not c["passed"]]
            basis = "partial evidence; missing: " + ", ".join(str(m) for m in missing)
        else:
            disposition = "inconclusive"
            basis = "none of the required visible values matched"
    elif rule.get("type") == "scene":
        scene_text = (answer_value(output, "scene_type") + " " + searchable(output)).lower()
        expected = [e.lower() for e in rule.get("expected_any", [])]
        if any(e in scene_text for e in expected):
            disposition = "used"
            basis = "expected scene type visible"
            checks.append({"name": "scene_type", "passed": True})
        else:
            disposition = "context-only"
            basis = "scene type does not match the expected scene"
            checks.append({"name": "scene_type", "passed": False})
    elif rule.get("type") == "promo":
        text = searchable(output)
        promo = any(k.lower() in text for k in rule.get("keywords", []))
        checks.append({"name": "promo_keywords", "passed": promo})
        if promo:
            disposition = "rejected"
            basis = "promotional overlay confirmed; not gameplay evidence"
        elif "gameplay" in text or "in-game" in text:
            disposition = "context-only"
            basis = "no promo overlay visible; frame is gameplay but not the claimed promo"
        else:
            disposition = "inconclusive"
            basis = "promotion/gameplay state unclear"
    else:
        disposition = model_disp
        basis = "model disposition (no deterministic rule)"
        checks.append({"name": "model_disposition", "passed": disposition in DISPOSITIONS})

    max_disp = group.get("max_disposition")
    if max_disp == "context-only" and disposition == "used":
        disposition = "context-only"
        basis += "; capped at context-only by plan policy"

    limitations = str(output.get("limitations") or "").strip()
    if forced:
        limitations = (limitations + " " if limitations else "") + (group.get("force_reason") or "")

    return {
        "disposition": disposition,
        "model_disposition": model_disp,
        "disposition_basis": basis,
        "confidence": confidence,
        "observation": str(output.get("observation") or "").strip(),
        "visible_text": normalize_list(output.get("visible_text")),
        "answers": output.get("answers") or {},
        "limitations": limitations,
        "checks": checks,
    }


# ---------------------------------------------------------------------------
# Boundary evaluation
# ---------------------------------------------------------------------------

def find_teams(text: str) -> set[str]:
    upper = (text or "").upper()
    found = set()
    for canonical, aliases in ALIASES.items():
        # Require token boundaries so short aliases such as "AE" do not match
        # inside ordinary words like "AERIAL" or "AEGIS".
        if any(re.search(rf"(?<![A-Z0-9]){re.escape(alias.upper())}(?![A-Z0-9])", upper)
               for alias in aliases):
            found.add(canonical)
    return found


def classify_pairing(teams_text: str, team_a: str, team_b: str) -> tuple[str, set[str]]:
    found = find_teams(teams_text)
    expected = {team_a.upper(), team_b.upper()}
    if not found:
        return "unknown", found
    if expected <= found:
        extras = found - expected
        return ("supported" if not extras else "supported-with-extras"), found
    if found & expected:
        return "partial", found
    return "contradicted", found


def scene_bucket(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ("klasemen", "standings", "league table", "ranking table")):
        return "standings"
    if any(k in t for k in ("schedule", "jadwal", "day's matches", "match schedule")):
        return "schedule"
    if any(k in t for k in ("map overview", "overhead map", "isometric overhead", "minimap overview")):
        return "map"
    if any(k in t for k in ("post-game", "post game", "player camera", "after the game")):
        return "post-game"
    if any(k in t for k in ("promo", "premium", "advertisement", "sponsor reel")):
        return "promo"
    if any(k in t for k in ("analyst", "desk", "caster panel", "studio panel", "commentary")):
        return "analyst"
    if any(k in t for k in ("interview", "host", "reporter")):
        return "interview"
    if any(k in t for k in ("draft pick in", "countdown", "pre-match", "pre match", "opening ceremony")):
        return "pre-match"
    if re.search(r"\bdraft\b", t):
        return "draft"
    if any(k in t for k in ("gameplay", "in-game", "in game", "teamfight", "top-down", "fight")):
        return "gameplay"
    if any(k in t for k in ("stage", "ceremony")):
        return "pre-match"
    return "unknown"


def sanitize_scene_text(text: str) -> str:
    """Drop clauses that explicitly deny the presence of the thing we are looking for."""
    parts = re.split(r"(?<=[.;])\s+", str(text or ""))
    keep = []
    for part in parts:
        if re.search(r"\b(no|not|without|absent|unclear|illegible|cannot|none)\b", part, re.I):
            continue
        keep.append(part)
    return " ".join(keep).strip()


def frame_scene_text(out: dict) -> str:
    answers = out.get("answers") or {}
    scene = str(answers.get("scene_type") or answers.get("scene") or "").strip()
    if scene:
        return scene
    return sanitize_scene_text(out.get("observation") or "")


def frame_team_text(out: dict) -> str:
    answers = out.get("answers") or {}
    for key in ("teams", "team_names", "team_pairing", "pairing", "teams_logos"):
        value = str(answers.get(key) or "").strip()
        if not value:
            continue
        if is_negative_answer(value):
            continue
        if re.search(r"\b(no|not)\b.{0,24}\b(legible|visible|readable|shown|identified)\b", value, re.I):
            continue
        if re.search(r"\b(illegible|unlabeled|unknown)\b", value, re.I) and " vs " not in value.lower():
            continue
        if find_teams(value):
            return value
    visible = " ".join(normalize_list(out.get("visible_text")))
    if find_teams(visible):
        return visible
    return sanitize_scene_text(out.get("observation") or "")


def mentions_multiple_matches(out: dict) -> bool:
    """True when the frame's own answers describe more than one match card.

    A pre-show schedule that names several fixtures cannot contradict the
    claimed pairing: the expected teams may still be present only as crests,
    while other matches supply the legible names.
    """
    answers = out.get("answers") or {}
    text = " ".join(str(answers.get(key) or "") for key in
                    ("match_label", "teams", "scoreboard"))
    labels = {re.sub(r"\s+", "", match.upper())
              for match in re.findall(r"\b(?:MATCH|M)\s*\d+\b", text, re.I)}
    return len(labels) > 1


def decide_boundary(boundary: dict, group_outputs: list[dict], related_outputs: list[dict],
                    frame_records: list[dict], related_records: list[dict]) -> dict:
    team_a = boundary["team_a"].upper()
    team_b = boundary["team_b"].upper()
    observations = []
    clocks = []
    per_frame = []
    for out in group_outputs:
        scene_text = frame_scene_text(out)
        team_text = frame_team_text(out)
        state, found = classify_pairing(team_text, team_a, team_b)
        if state == "contradicted" and mentions_multiple_matches(out):
            state = "unknown"
        bucket = scene_bucket(scene_text)
        clock = str((out.get("answers") or {}).get("clock_or_countdown", "") or
                    (out.get("answers") or {}).get("clock", "") or
                    (out.get("answers") or {}).get("clock_countdown", ""))
        per_frame.append({"state": state, "found": found, "bucket": bucket,
                          "scene": scene_text, "clock": clock, "teams": team_text,
                          "observation": str(out.get("observation", ""))})
        observations.append(per_frame[-1]["observation"])
        clocks.append(clock)

    def aggregate(frames: list[dict]) -> tuple[str, str, set[str], dict | None]:
        states = [f["state"] for f in frames]
        if any(s == "contradicted" for s in states):
            pairing = "contradicted"
        elif any(s in ("supported", "supported-with-extras") for s in states):
            pairing = "supported"
        elif any(s == "partial" for s in states):
            pairing = "partial"
        else:
            pairing = "unknown"
        found_all = set()
        for f in frames:
            found_all |= f["found"]
        ranked = sorted(frames, key=lambda f: ({"contradicted": 0, "supported": 1,
                                                "supported-with-extras": 2, "partial": 3,
                                                "unknown": 4}[f["state"]],
                                               {"gameplay": 0, "draft": 1, "pre-match": 2,
                                                "interview": 3, "analyst": 4, "map": 5,
                                                "standings": 6, "schedule": 7, "promo": 8,
                                                "post-game": 9, "unknown": 10}[f["bucket"]]))
        best = ranked[0] if ranked else None
        bucket = best["bucket"] if best else "unknown"
        return pairing, bucket, found_all, best

    pairing, bucket, found_all, best = aggregate(per_frame)
    related_pairing, related_bucket, related_found, related_best = aggregate(
        [{"state": classify_pairing(frame_team_text(o), team_a, team_b)[0],
          "found": classify_pairing(frame_team_text(o), team_a, team_b)[1],
          "bucket": scene_bucket(frame_scene_text(o)),
          "scene": frame_scene_text(o),
          "clock": str((o.get("answers") or {}).get("clock_or_countdown", "") or
                       (o.get("answers") or {}).get("clock", "")),
          "teams": frame_team_text(o),
          "observation": str(o.get("observation", ""))}
         for o in related_outputs]
    ) if related_outputs else ("unknown", "unknown", set(), None)

    pairing_source = "primary"
    if pairing == "unknown" and related_pairing in ("supported", "supported-with-extras"):
        # A probe at a different timestamp can corroborate the pairing but
        # cannot contradict the candidate boundary's own frames.
        pairing = related_pairing
        pairing_source = "related"
        found_all |= related_found
        if bucket == "unknown" and related_best:
            bucket = related_bucket
    elif pairing == "unknown" and related_best:
        # A related frame can supply the scene even when it cannot supply the pairing.
        if bucket == "unknown":
            bucket = related_bucket

    if bucket in ("standings", "schedule"):
        series_disp = "context-only"
        series_evidence = f"scene={bucket}; visible teams={sorted(found_all) or 'none'}"
    elif bucket == "map":
        series_disp = "inconclusive"
        series_evidence = f"map overview; visible teams={sorted(found_all) or 'none'}"
    elif pairing == "contradicted":
        series_disp = "rejected"
        series_evidence = f"visible teams={sorted(found_all)} do not include {team_a} and {team_b}"
    elif pairing in ("supported", "supported-with-extras"):
        series_disp = "used"
        series_evidence = f"visible teams include {team_a} and {team_b}"
        if pairing_source == "related":
            series_evidence += " (related frames at a nearby timestamp)"
    elif pairing == "partial":
        series_disp = "context-only"
        series_evidence = f"only part of the pairing is visible: {sorted(found_all)}"
    else:
        series_disp = "inconclusive"
        series_evidence = "no legible team pairing"

    scene_text_all = " | ".join(f["scene"] for f in per_frame if f["scene"])
    if related_best and related_best["scene"]:
        scene_text_all += " | " + related_best["scene"]
    clock_text = " | ".join(c for c in clocks if c and not is_negative_answer(c))
    match_labels = [str((o.get("answers") or {}).get("match_label", "")).strip() for o in group_outputs]
    match_label = " ".join(m for m in match_labels
                           if m and not is_negative_answer(m) and not m.lower().startswith("none"))
    if bucket in ("standings", "schedule", "promo", "post-game"):
        game1_disp = "rejected"
        game1_evidence = f"scene={bucket} is not a game-1 start"
    elif re.search(r"\bGAME\s*([2-9])\b", scene_text_all + " " + match_label, re.I):
        # A later game on screen means game 1 already happened; the candidate
        # cannot be the game-1 start even when the pairing is correct.
        later_game = re.search(r"\bGAME\s*([2-9])\b", scene_text_all + " " + match_label, re.I).group(1)
        game1_disp = "rejected"
        game1_evidence = f"frame shows GAME {later_game}, not game 1"
    elif bucket == "map":
        game1_disp = "inconclusive"
        game1_evidence = "map overview has no draft, clock, or game-1 start indicator"
    elif (boundary.get("promotion_requires_same_frame")
          and any(re.search(r"\b0{1,2}:0{2}\b", f["clock"]) for f in per_frame)
          and not any(f["state"] in ("supported", "supported-with-extras")
                      and re.search(r"\b0{1,2}:0{2}\b", f["clock"]) for f in per_frame)):
        game1_disp = "context-only"
        game1_evidence = ("00:00 clock visible, but not in the same frame as the claimed "
                          "pairing; countdown/draft/adjacent evidence is confirmation only")
    elif re.search(r"\b0{1,2}:0{2}\b", clock_text):
        game1_disp = "used"
        game1_evidence = f"game clock at zero: {clock_text}"
    elif bucket == "draft":
        game1_disp = "context-only"
        game1_evidence = "draft phase visible; draft screens are confirmation only, not a 00:00 start"
    elif (bucket in ("pre-match", "interview", "analyst")
          and boundary.get("candidate_start_seconds") is not None
          and boundary["candidate_start_seconds"] <= 600):
        game1_disp = "rejected"
        game1_evidence = ("pre-show segment at the 300s candidate offset; "
                          "no draft or game clock")
    elif bucket == "gameplay":
        game1_disp = "context-only"
        game1_evidence = "gameplay is in progress; the start is not visible"
    elif re.search(r"\b\d{1,2}:\d{2}\b", clock_text):
        game1_disp = "context-only"
        game1_evidence = f"countdown/clock present but no game start: {clock_text}"
    elif bucket in ("pre-match", "interview", "analyst") and (match_label.strip() or clock_text.strip()):
        game1_disp = "context-only"
        game1_evidence = "pre-match/desk segment; no draft or game clock"
    else:
        game1_disp = "inconclusive"
        game1_evidence = "no draft, game clock at zero, or start indicator"

    if boundary.get("probe_only"):
        if series_disp == "rejected":
            series_disp = "context-only"
            series_evidence = ("probe frames show a different series/game; the canonical series pairing "
                               "is not contradicted by this probe")
        if game1_disp == "rejected":
            game1_disp = "context-only"
            game1_evidence = ("probe frames are a later game/preview; the game-1 start is not shown "
                              "(probe-only, not a canonical rejection)")

    pre_show = bucket == "schedule" and re.search(r"\b([1-9]\d):\d{2}\b", clock_text)
    if series_disp == "rejected" or game1_disp == "rejected":
        overall = "rejected"
    elif series_disp == "used" and game1_disp == "used":
        overall = "used"
    elif series_disp == "used":
        overall = "context-only"
    elif pre_show:
        overall = "rejected"
    elif series_disp == "context-only":
        overall = "context-only"
    else:
        overall = "inconclusive"

    related_note = None
    if related_outputs:
        related_note = (
            f"related frames: pairing={related_pairing}; scene={related_bucket}; "
            f"teams={sorted(related_found) or 'none'}; "
            + " ".join(str(o.get("observation", "")) for o in related_outputs)[:300]
        )

    observation = " ".join(o for o in observations if o)[:1200]
    limitation = ("Still images cannot prove a continuous transition. The game-1 start is only supported "
                  "when a draft/zero-clock state is visibly present; a pre-match countdown is not a start.")
    if pairing_source == "related":
        limitation += " The team pairing is confirmed by related frames at a nearby timestamp, not by the candidate frame itself."
    status_effect = "no_change"
    if overall == "rejected":
        status_effect = "candidate_rejected"
    elif overall == "used":
        status_effect = "visual_confirmation"
    elif overall == "context-only":
        status_effect = "partial_context_only"

    return {
        "boundary_id": boundary["boundary_id"],
        "match_detail_id": boundary["match_detail_id"],
        "source_id": boundary["source_id"],
        "team_a": boundary["team_a"],
        "team_b": boundary["team_b"],
        "candidate_start_seconds": boundary.get("candidate_start_seconds"),
        "claim": boundary.get("claim"),
        "frame_group": boundary.get("frame_group"),
        "frame_ids": [r["frame_id"] for r in frame_records],
        "frame_sha256": [r["screenshot_sha256"] for r in frame_records],
        "related_frame_ids": [r["frame_id"] for r in related_records],
        "related_frame_sha256": [r["screenshot_sha256"] for r in related_records],
        "series_pairing": {
            "disposition": series_disp,
            "evidence": series_evidence,
            "confidence": "high" if pairing in ("supported", "contradicted") and bucket not in ("standings", "map") else "med",
            "source": pairing_source,
        },
        "game1_start": {
            "disposition": game1_disp,
            "evidence": game1_evidence,
            "confidence": "high" if bucket != "unknown" else "low",
        },
        "disposition": overall,
        "observation": observation,
        "limitations": limitation,
        "related_observation": related_note,
        "status_effect": status_effect,
    }


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------

def make_smoke_image() -> bytes:
    try:
        from PIL import Image, ImageDraw
    except Exception as exc:  # pragma: no cover
        raise SystemExit("Pillow is required for the smoke test") from exc
    img = Image.new("RGB", (720, 360), (12, 18, 32))
    draw = ImageDraw.Draw(img)
    draw.rectangle([24, 24, 696, 336], outline=(0, 220, 160), width=4)
    draw.text((60, 70), "DEEPSEEK VISION", fill=(255, 255, 255))
    draw.text((60, 140), "SMOKE TEST 4729", fill=(255, 214, 10))
    draw.text((60, 210), "TOP LEFT: ORANGE CIRCLE", fill=(255, 140, 0))
    draw.ellipse([560, 230, 660, 330], fill=(255, 140, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def run_smoke(args) -> int:
    key, key_source = load_api_key(args.opencode_credential, args.opencode_base)
    image = make_smoke_image()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    image_path = RAW_DIR / "smoke-test.png"
    image_path.write_bytes(image)
    prompt = (
        "Inspect this synthetic test image. Transcribe every line of text exactly. Then state the color "
        "and position of the circular shape. Return ONLY JSON with keys: text_lines (array), shape_color, "
        "shape_position, observation. Do not trust the text label about the shape; report what you see."
    )
    parsed, call = call_with_retry(key, [image], prompt, max_tokens=4000,
                                   call_id="smoke-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                                   group_id="smoke")
    text = " ".join(normalize_list(parsed.get("text_lines"))).lower()
    color = str(parsed.get("shape_color", "")).lower()
    position = str(parsed.get("shape_position", "")).lower()
    checks = {
        "text_deepseek_vision": "deepseek vision" in text,
        "text_smoke_test_4729": "smoke test 4729" in text,
        "shape_orange": "orange" in color,
        "shape_bottom_right": any(k in position for k in ("bottom-right", "bottom right", "lower right",
                                                          "lower-right")) or
                              ("bottom" in position and "right" in position),
    }
    passed = all(checks.values())
    raw_path = RAW_DIR / f"{call['call_id']}.json"
    atomic_write_json(raw_path, call)
    record = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "reviewer": REVIEWER,
        "model": call.get("model", ACTIVE_BACKEND["model"]),
        "provider": call.get("provider", ACTIVE_BACKEND["provider"]),
        "api_base": ACTIVE_BACKEND["api_base"],
        "transport": ACTIVE_BACKEND["mode"],
        "session_id": call.get("session_id"),
        "key_source": key_source,
        "status": "passed" if passed else "failed",
        "image_path": rel(image_path),
        "image_sha256": sha256_bytes(image),
        "api_request_id": call.get("request_id"),
        "usage": call.get("usage"),
        "checks": checks,
        "observation": parsed.get("observation"),
        "shape_color": parsed.get("shape_color"),
        "shape_position": parsed.get("shape_position"),
        "text_lines": parsed.get("text_lines"),
        "raw_response_path": rel(raw_path),
        "raw_response_sha256": sha256_file(raw_path),
    }
    atomic_write_json(Path(args.out), record)
    print(json.dumps(record, indent=2))
    return 0 if passed else 1


# ---------------------------------------------------------------------------
# Full review
# ---------------------------------------------------------------------------

def ensure_smoke(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"smoke record missing: {path}; run the smoke command first")
    smoke = load_json(path)
    if smoke.get("status") != "passed":
        raise SystemExit(f"smoke test did not pass: {path}")
    return smoke


def prepare_group(group: dict) -> tuple[list[bytes], list[dict], list[dict]]:
    images = []
    sidecars = []
    metas = []
    for frame in group["frames"]:
        path, data, side, meta = prepare_frame(frame)
        images.append(data)
        sidecars.append(side)
        metas.append(meta)
    return images, sidecars, metas


def group_hash(group: dict, metas: list[dict]) -> str:
    return sha256_bytes("".join(m["screenshot_sha256"] for m in metas).encode())


def frame_record(group: dict, meta: dict, output: dict, evaluation: dict,
                 call: dict, reviewed_at: str) -> dict:
    return {
        **meta,
        "claim_id": group.get("claim_id"),
        "group_id": group.get("group_id"),
        "claim": group.get("claim"),
        "review_status": "reviewed",
        "reviewer": REVIEWER,
        "reviewed_at": reviewed_at,
        "model": call.get("model", ACTIVE_BACKEND["model"]),
        "provider": call.get("provider", ACTIVE_BACKEND["provider"]),
        "transport": call.get("transport", ACTIVE_BACKEND["mode"]),
        "session_id": call.get("session_id"),
        "api_request_id": call.get("request_id"),
        "api_call_id": call.get("call_id"),
        "disposition": evaluation["disposition"],
        "model_disposition": evaluation["model_disposition"],
        "disposition_basis": evaluation["disposition_basis"],
        "confidence": evaluation["confidence"],
        "observation": evaluation["observation"],
        "visible_text": evaluation["visible_text"],
        "answers": evaluation["answers"],
        "limitations": evaluation["limitations"],
        "checks": evaluation["checks"],
        "usage": call.get("usage", {}),
    }


def merge_group_outputs(group: dict, parsed, n: int) -> list[dict]:
    if n == 1:
        if isinstance(parsed, list):
            if len(parsed) != 1:
                raise BadResponse(f"expected one object, got list of {len(parsed)}")
            parsed = parsed[0]
        if not isinstance(parsed, dict):
            raise BadResponse(f"expected object, got {type(parsed).__name__}")
        return [parsed]
    if isinstance(parsed, dict):
        for key in ("frames", "results", "images", "items"):
            if isinstance(parsed.get(key), list):
                parsed = parsed[key]
                break
    if not isinstance(parsed, list):
        raise BadResponse(f"expected array of {n}, got {type(parsed).__name__}")
    if len(parsed) != n:
        raise BadResponse(f"expected {n} objects, got {len(parsed)}")
    out = []
    for i, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise BadResponse(f"item {i} is not an object")
        item = dict(item)
        item.setdefault("image_index", i)
        out.append(item)
    return out


def run_group(key: str, group: dict, existing: dict | None = None) -> tuple[list[dict], dict, bool]:
    images, sidecars, metas = prepare_group(group)
    n = len(images)
    if existing:
        return existing["frames"], existing["call"], True
    call_id = f"{group['group_id']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    prompt = build_prompt(group, n)
    try:
        parsed, call = call_with_retry(key, images, prompt, max_tokens=10000 if n > 1 else 6000,
                                       call_id=call_id, group_id=group["group_id"])
        outputs = merge_group_outputs(group, parsed, n)
    except BadResponse:
        # Split fallback: review each image independently. This avoids losing the whole group
        # when a multi-image response is malformed.
        outputs = []
        call = {"call_id": call_id, "group_id": group["group_id"],
                "provider": ACTIVE_BACKEND["provider"], "model": ACTIVE_BACKEND["model"],
                "transport": ACTIVE_BACKEND["mode"], "session_id": None,
                "request_id": None, "usage": {}, "finish_reason": "split",
                "fallback_split": True, "attempts": []}
        for index, image in enumerate(images):
            single_prompt = build_prompt(group, 1) + f"\nThis is image {index + 1} of {n} from the group; describe only this image."
            single_id = f"{call_id}-split{index}"
            parsed, single_call = call_with_retry(key, [image], single_prompt, max_tokens=6000,
                                                  call_id=single_id, group_id=group["group_id"])
            if isinstance(parsed, list):
                parsed = parsed[0] if len(parsed) == 1 else {"observation": str(parsed),
                                                             "visible_text": [],
                                                             "answers": {}}
            parsed = dict(parsed)
            parsed["image_index"] = index
            outputs.append(parsed)
            call["attempts"].append(single_call)
            if not call["request_id"]:
                call["request_id"] = single_call.get("request_id")
            for k, v in (single_call.get("usage") or {}).items():
                if isinstance(v, int):
                    call["usage"][k] = call["usage"].get(k, 0) + v
    reviewed_at = now_iso()
    records = []
    for meta, output in zip(metas, outputs):
        evaluation = evaluate_frame(group, output, meta)
        records.append(frame_record(group, meta, output, evaluation, call, reviewed_at))
    # Persist the raw API call for audit.
    raw_path = RAW_DIR / f"{call_id}.json"
    payload = dict(call)
    payload["prompt"] = prompt
    payload["parsed"] = outputs
    atomic_write_json(raw_path, payload)
    call["raw_response_path"] = rel(raw_path)
    call["raw_response_sha256"] = sha256_file(raw_path)
    for rec in records:
        rec["raw_response_path"] = call["raw_response_path"]
        rec["raw_response_sha256"] = call["raw_response_sha256"]
    return records, call, False


def summarize(frames: list[dict], boundaries: list[dict]) -> dict:
    frame_counts = {d: 0 for d in sorted(DISPOSITIONS)}
    for f in frames:
        frame_counts[f.get("disposition", "inconclusive")] = frame_counts.get(f.get("disposition", "inconclusive"), 0) + 1
    boundary_counts = {d: 0 for d in sorted(DISPOSITIONS)}
    for b in boundaries:
        boundary_counts[b.get("disposition", "inconclusive")] = boundary_counts.get(b.get("disposition", "inconclusive"), 0) + 1
    return {
        "frames_reviewed": len(frames),
        "frame_dispositions": frame_counts,
        "boundary_reviews": len(boundaries),
        "boundary_dispositions": boundary_counts,
        "candidate_rejections": sum(1 for b in boundaries if b.get("status_effect") == "candidate_rejected"),
        "visual_confirmations": sum(1 for b in boundaries if b.get("status_effect") == "visual_confirmation"),
    }


def run_review(args) -> int:
    plan_path = Path(args.plan)
    plan = load_json(plan_path)
    smoke = ensure_smoke(Path(args.smoke))
    key, key_source = load_api_key(args.opencode_credential, args.opencode_base)
    out_path = Path(args.out)

    existing = {}
    existing_calls = []
    preserved_backlog = None
    if args.resume and out_path.exists():
        old = load_json(out_path)
        existing_calls = old.get("api_calls", [])
        preserved_backlog = old.get("backlog")
        by_group = {}
        for rec in old.get("frames", []):
            by_group.setdefault(rec.get("group_id"), []).append(rec)
        for group in plan["groups"]:
            recs = by_group.get(group["group_id"], [])
            if len(recs) != len(group["frames"]):
                continue
            hashes = {r.get("screenshot_sha256") for r in recs}
            local_hashes = set()
            ok = True
            for frame in group["frames"]:
                p = repo_path(frame["path"])
                if not p.exists():
                    ok = False
                    break
                local_hashes.add(sha256_file(p))
            if ok and hashes == local_hashes and all(r.get("review_status") == "reviewed" for r in recs):
                call = next((c for c in existing_calls if c.get("call_id") == recs[0].get("api_call_id")), None)
                if call:
                    existing[group["group_id"]] = {"frames": recs, "call": call}

    frames_all = []
    calls_all = []
    boundary_reviews = []
    group_outputs = {}
    group_metas = {}
    for group in plan["groups"]:
        records, call, reused = run_group(key, group, existing.get(group["group_id"]))
        frames_all.extend(records)
        group_outputs[group["group_id"]] = [r.get("answers", {}) for r in records]
        group_metas[group["group_id"]] = records
        if not reused:
            calls_all.append(call)
        # Build a partial ledger after each group so a crash does not lose progress.
        partial = {
            "schema_version": 1,
            "generated_at": now_iso(),
            "reviewer": REVIEWER,
            "model": ACTIVE_BACKEND["model"],
            "provider": ACTIVE_BACKEND["provider"],
            "api_base": ACTIVE_BACKEND["api_base"],
            "transport": ACTIVE_BACKEND["mode"],
            "prompt_version": PROMPT_VERSION,
            "review_mode": "api-pixel-inspection-only",
            "human_review": False,
            "key_source": key_source,
            "plan_path": rel(plan_path),
            "plan_sha256": sha256_text_lf(plan_path),
            "smoke_test": smoke,
            "frames": frames_all,
            "api_calls": existing_calls + calls_all,
            "boundary_reviews": [],
            "unresolved": plan.get("unresolved", []),
            "backlog": preserved_backlog,
            "summary": summarize(frames_all, []),
        }
        atomic_write_json(out_path, partial)
        print(f"reviewed {group['group_id']}: {len(records)} frame(s)")

    # Boundary reviews use the frame answers from their primary and related groups.
    for boundary in plan.get("boundary_claims", []):
        gid = boundary["frame_group"]
        records = group_metas.get(gid, [])
        related_records = []
        for rid in boundary.get("related_groups", []):
            related_records.extend(group_metas.get(rid, []))
        boundary_reviews.append(decide_boundary(boundary, records, related_records,
                                                 records, related_records))

    ledger = {
        "schema_version": 1,
        "generated_at": now_iso(),
        "reviewer": REVIEWER,
        "model": ACTIVE_BACKEND["model"],
        "provider": ACTIVE_BACKEND["provider"],
        "api_base": ACTIVE_BACKEND["api_base"],
        "transport": ACTIVE_BACKEND["mode"],
        "models_used": sorted({f.get("model") for f in frames_all if f.get("model")}),
        "prompt_version": PROMPT_VERSION,
        "review_mode": "api-pixel-inspection-only",
        "human_review": False,
        "key_source": key_source,
        "plan_path": rel(plan_path),
        "plan_sha256": sha256_text_lf(plan_path),
        "smoke_test": smoke,
        "contract": {
            "reviewed_requires": "parsed DeepSeek API response for the exact screenshot hash",
            "dispositions": sorted(DISPOSITIONS),
            "no_human_review": True,
            "still_image_limit": "A still frame supports only what is visible at that instant; temporal "
                                 "claims require ordered frames and are not promoted from this ledger alone.",
        },
        "frames": frames_all,
        "api_calls": existing_calls + calls_all,
        "boundary_reviews": boundary_reviews,
        "unresolved": plan.get("unresolved", []),
        "backlog": preserved_backlog,
        "summary": summarize(frames_all, boundary_reviews),
    }
    atomic_write_json(out_path, ledger)
    print(json.dumps(ledger["summary"], indent=2))
    print(f"wrote {out_path}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    smoke = sub.add_parser("smoke", help="run the minimal DeepSeek vision API smoke test")
    smoke.add_argument("--out", default=str(DEFAULT_SMOKE))
    smoke.add_argument("--backend", choices=sorted(BACKENDS), default="direct")
    smoke.add_argument("--opencode-credential", action="store_true")
    smoke.add_argument("--opencode-base", default="http://127.0.0.1:28894")
    smoke.set_defaults(func=run_smoke)

    run = sub.add_parser("run", help="review all frames in the plan")
    run.add_argument("--plan", default=str(DEFAULT_PLAN))
    run.add_argument("--out", default=str(DEFAULT_OUT))
    run.add_argument("--smoke", default=str(DEFAULT_SMOKE))
    run.add_argument("--backend", choices=sorted(BACKENDS), default="direct")
    run.add_argument("--opencode-credential", action="store_true")
    run.add_argument("--opencode-base", default="http://127.0.0.1:28894")
    run.add_argument("--resume", action="store_true")
    run.set_defaults(func=run_review)

    args = parser.parse_args(argv)
    global ACTIVE_BACKEND
    ACTIVE_BACKEND = dict(BACKENDS[args.backend])
    if args.opencode_base:
        if args.backend == "opencode-session":
            ACTIVE_BACKEND["api_base"] = args.opencode_base
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
