#!/usr/bin/env python3
"""Capture full-frame screenshots at requested YouTube/local-video timestamps.

Why this backend: on this machine, yt-dlp/FFmpeg section downloads from the long
MPL VODs stalled while the browser player sought reliably. The tool therefore
uses Playwright's Chromium player for YouTube VODs and FFmpeg for local files.
It never downloads a full broadcast; YouTube frames are captured from the player
at the requested time. Every frame gets a sidecar with the canonical URL,
timestamp link, requested/actual time, method, versions, output hash and errors.

Usage:
    python tools/video_frames.py --source-id src-s18-w01d01 `
      --timestamps 00:57:49,00:58:05 --around-seconds 2 --contact-sheet

    python tools/video_frames.py --url "https://www.youtube.com/watch?v=VIDEOID" `
      --timestamp 00:12:34

    python tools/video_frames.py --local-video fixture.mp4 --timestamps 0,2,4

Outputs default to analysis/cache/video-frames/ (gitignored). The tool reports
success/failure per requested frame and exits nonzero if any requested frame
failed. A downloaded/captured frame is never labelled "verified"; visual review
is a separate, explicit step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO / "analysis" / "sources" / "source-manifest.json"
DEFAULT_CACHE = REPO / "analysis" / "cache" / "video-frames"
VIDEO_ID_RE = re.compile(r"[A-Za-z0-9_-]{11}")
TIME_RE = re.compile(r"^(?:(\d+):)?(?:(\d{1,2}):)?(\d{1,2}(?:\.\d+)?)$")


class FrameError(ValueError):
    pass


def parse_timestamp(value: str | int | float) -> float:
    """Parse HH:MM:SS, MM:SS or seconds into non-negative seconds."""
    if isinstance(value, (int, float)):
        seconds = float(value)
        if seconds < 0 or seconds != seconds:
            raise FrameError(f"invalid timestamp: {value!r}")
        return seconds
    text = str(value).strip()
    if not text:
        raise FrameError("empty timestamp")
    if text.startswith("-"):
        raise FrameError(f"negative timestamp: {text!r}")
    if text.replace(".", "", 1).isdigit():
        return float(text)
    parts = text.split(":")
    if len(parts) > 3 or any(not p.isdigit() for p in parts):
        raise FrameError(f"invalid timestamp: {text!r}")
    nums = [int(p) for p in parts]
    if len(nums) == 1:
        seconds = nums[0]
    elif len(nums) == 2:
        seconds = nums[0] * 60 + nums[1]
    else:
        seconds = nums[0] * 3600 + nums[1] * 60 + nums[2]
    return float(seconds)


def format_timestamp(seconds: float) -> str:
    seconds = max(0, float(seconds))
    h = int(seconds // 3600)
    m = int(seconds % 3600 // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def extract_video_id(value: str) -> str:
    text = value.strip()
    if VIDEO_ID_RE.fullmatch(text):
        return text
    patterns = [
        r"(?:v=|/v/|/embed/|/shorts/|/live/|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"[?&]v=([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    raise FrameError(f"cannot extract a YouTube video ID from {value!r}")


def canonical_url(video_id: str) -> str:
    if not VIDEO_ID_RE.fullmatch(video_id):
        raise FrameError(f"invalid video id {video_id!r}")
    return f"https://www.youtube.com/watch?v={video_id}"


def timestamp_link(video_id: str, seconds: float) -> str:
    return f"{canonical_url(video_id)}&t={int(max(0, seconds))}s"


def safe_component(value: str, fallback: str = "video") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value or "")).strip("._-")
    if not cleaned or cleaned in {".", ".."}:
        cleaned = fallback
    return cleaned[:80]


def build_plan(timestamps: Iterable[float], around_seconds: float = 0.0) -> list[dict]:
    if around_seconds < 0:
        raise FrameError("around-seconds must be >= 0")
    plan = []
    for requested in timestamps:
        offsets = [0.0]
        if around_seconds:
            offsets = [-float(around_seconds), 0.0, float(around_seconds)]
        for offset in offsets:
            target = max(0.0, float(requested) + offset)
            key = round(target, 3)
            if any(round(row["capture_seconds"], 3) == key for row in plan):
                continue
            plan.append(
                {
                    "requested_seconds": float(requested),
                    "offset_seconds": float(target - float(requested)),
                    "capture_seconds": target,
                }
            )
    return plan


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tool_versions(browser_version: str | None = None) -> dict:
    versions = {"python": sys.version.split()[0]}
    try:
        import playwright

        versions["playwright"] = getattr(playwright, "__version__", "unknown")
    except Exception:
        versions["playwright"] = None
    versions["chromium"] = browser_version
    try:
        out = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT, timeout=20)
        versions["ffmpeg"] = out.decode("utf-8", "replace").splitlines()[0]
    except Exception:
        versions["ffmpeg"] = None
    return versions


def _frame_name(source_key: str, row: dict) -> str:
    at = format_timestamp(row["capture_seconds"]).replace(":", "").replace(".", "_")
    offset = int(round(row["offset_seconds"]))
    sign = "p" if offset >= 0 else "m"
    return f"{source_key}_at_{at}_{sign}{abs(offset):03d}.png"


def _write_sidecar(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _base_payload(
    source: dict | None,
    source_id: str | None,
    video_id: str | None,
    row: dict,
    method: str,
    versions: dict,
) -> dict:
    return {
        "schema_version": 1,
        "source_id": source_id,
        "source_title": (source or {}).get("video_title"),
        "video_id": video_id,
        "video_url": canonical_url(video_id) if video_id else None,
        "timestamp_link": timestamp_link(video_id, row["capture_seconds"]) if video_id else None,
        "requested_seconds": row["requested_seconds"],
        "offset_seconds": row["offset_seconds"],
        "capture_seconds": row["capture_seconds"],
        "method": method,
        "tool_versions": versions,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "review_status": "not-reviewed",
        "status": "failed",
        "error": None,
        "warnings": [],
    }


def capture_local(
    local_video: Path,
    plan: list[dict],
    out_dir: Path,
    source: dict | None = None,
    source_id: str | None = None,
    reuse: bool = True,
) -> list[dict]:
    if not local_video.exists():
        raise FrameError(f"local video not found: {local_video}")
    try:
        ffprobe = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
             "default=noprint_wrappers=1:nokey=1", str(local_video)],
            stderr=subprocess.STDOUT, timeout=30,
        ).decode("utf-8", "replace").strip()
        duration = float(ffprobe)
    except Exception:
        duration = None
    versions = tool_versions()
    key = safe_component(source_id or local_video.stem)
    frames = []
    for row in plan:
        out = out_dir / key / _frame_name(key, row)
        out.parent.mkdir(parents=True, exist_ok=True)
        sidecar = out.with_suffix(".json")
        payload = _base_payload(source, source_id, None, row, "ffmpeg-local-frame", versions)
        payload["source_path"] = str(local_video)
        payload["duration_seconds"] = duration
        payload["output_path"] = str(out.relative_to(REPO)) if out.is_relative_to(REPO) else str(out)
        if reuse and out.exists() and sidecar.exists():
            try:
                prior = json.loads(sidecar.read_text(encoding="utf-8"))
                if prior.get("status") == "succeeded":
                    prior["reused"] = True
                    frames.append(prior)
                    continue
            except Exception:
                pass
        if duration is not None and row["capture_seconds"] > duration + 0.5:
            payload["error"] = f"timestamp beyond duration ({row['capture_seconds']} > {duration})"
            _write_sidecar(sidecar, payload)
            frames.append(payload)
            continue
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss",
            f"{row['capture_seconds']:.3f}", "-i", str(local_video), "-frames:v", "1",
            "-y", str(out),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 or not out.exists() or out.stat().st_size < 100:
            payload["error"] = (result.stderr or "ffmpeg produced no frame")[-800:]
        else:
            payload.update(
                {
                    "status": "succeeded",
                    "actual_seconds": row["capture_seconds"],
                    "output_sha256": sha256_file(out),
                    "output_bytes": out.stat().st_size,
                }
            )
        _write_sidecar(sidecar, payload)
        frames.append(payload)
    return frames


def capture_youtube(
    video_id: str,
    plan: list[dict],
    out_dir: Path,
    source: dict | None = None,
    source_id: str | None = None,
    headed: bool = False,
    reuse: bool = True,
) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        raise FrameError("Python Playwright is required for the YouTube backend") from exc
    key = safe_component(source_id or video_id)
    out_dir = out_dir / key
    out_dir.mkdir(parents=True, exist_ok=True)
    first = plan[0]["capture_seconds"] if plan else 0
    frames = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        versions = tool_versions(browser.version)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            page.goto(
                f"{canonical_url(video_id)}&t={int(first)}s",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            page.wait_for_selector("video", timeout=60000)
            page.wait_for_function(
                "() => { const v=document.querySelector('video'); return v && v.readyState >= 2; }",
                timeout=60000,
            )
            page.wait_for_timeout(3000)
            if not page.locator("video").is_visible():
                raise FrameError("YouTube video element is not visible")
            for row in plan:
                out = out_dir / _frame_name(key, row)
                sidecar = out.with_suffix(".json")
                payload = _base_payload(
                    source, source_id, video_id, row, "playwright-chromium-video-element", versions
                )
                payload["output_path"] = (
                    str(out.relative_to(REPO)) if out.is_relative_to(REPO) else str(out)
                )
                if reuse and out.exists() and sidecar.exists():
                    try:
                        prior = json.loads(sidecar.read_text(encoding="utf-8"))
                        if prior.get("status") == "succeeded":
                            prior["reused"] = True
                            frames.append(prior)
                            continue
                    except Exception:
                        pass
                try:
                    # Ads are never a gameplay frame. Try to wait for a
                    # pre-roll/mid-roll to clear; the final screenshot check
                    # below still rejects an ad/promo if the wait expires.
                    try:
                        page.wait_for_function(
                            "() => !document.querySelector('.ad-showing')",
                            timeout=15000,
                        )
                    except Exception:
                        payload["warnings"].append("ad-state wait timed out")

                    def seek(t: float) -> dict:
                        return page.evaluate(
                            """(t) => new Promise((resolve) => {
                                const v=document.querySelector('video');
                                if (!v) return resolve({error:'no-video'});
                                v.muted=true; v.controls=false;
                                v.currentTime=t;
                                v.play().catch(()=>{});
                                setTimeout(() => {
                                  v.pause();
                                  resolve({
                                    t:v.currentTime, duration:v.duration, ready:v.readyState,
                                    width:v.videoWidth, height:v.videoHeight,
                                    title:document.title, url:location.href
                                  });
                                }, 1600);
                            })""",
                            t,
                        )

                    actual = seek(row["capture_seconds"])
                    if (
                        actual.get("error")
                        or actual.get("ready", 0) < 2
                        or abs(float(actual.get("t", -1)) - row["capture_seconds"]) > 2.5
                    ):
                        # Long VOD seeks can leave the paused player unloaded.
                        # Retry from a fresh player positioned at the target.
                        page.goto(
                            f"{canonical_url(video_id)}&t={int(row['capture_seconds'])}s",
                            wait_until="domcontentloaded",
                            timeout=60000,
                        )
                        page.wait_for_selector("video", timeout=60000)
                        page.wait_for_function(
                            "() => { const v=document.querySelector('video'); "
                            "return v && v.readyState >= 2; }",
                            timeout=60000,
                        )
                        page.wait_for_timeout(2500)
                        try:
                            page.wait_for_function(
                                "() => !document.querySelector('.ad-showing')",
                                timeout=15000,
                            )
                        except Exception:
                            payload["warnings"].append("ad-state retry wait timed out")
                        actual = seek(row["capture_seconds"])
                    page.wait_for_timeout(700)
                    overlay = page.evaluate(
                        """() => {
                            const v=document.querySelector('video');
                            const ad=!!document.querySelector('.ad-showing');
                            if (!v) return {ad:ad, promo:false};
                            const vr=v.getBoundingClientRect();
                            const bad=/YouTube Premium|Dapatkan YouTube|tanpa iklan|No ads/i;
                            let promo=false;
                            document.querySelectorAll('body *').forEach(el => {
                                if (promo || el.children.length) return;
                                const text=(el.innerText||'').trim();
                                if (!text || text.length > 140 || !bad.test(text)) return;
                                const r=el.getBoundingClientRect();
                                if (r.width < 20 || r.height < 10) return;
                                if (r.right < vr.left || r.left > vr.right || r.bottom < vr.top || r.top > vr.bottom) return;
                                promo=true;
                            });
                            return {ad:ad, promo:promo};
                        }"""
                    )
                    if overlay.get("ad") or overlay.get("promo"):
                        payload["error"] = (
                            "advertisement/promotional overlay showing instead of requested frame"
                        )
                    elif actual.get("error"):
                        payload["error"] = actual["error"]
                    elif actual.get("ready", 0) < 2:
                        payload["error"] = f"video not ready (readyState={actual.get('ready')})"
                    elif abs(float(actual.get("t", -1)) - row["capture_seconds"]) > 2.5:
                        payload["error"] = (
                            f"actual time {actual.get('t')} differs from requested "
                            f"{row['capture_seconds']}"
                        )
                    else:
                        page.locator("video").screenshot(path=str(out), type="png")
                        if not out.exists() or out.stat().st_size < 20000:
                            payload["error"] = "screenshot missing or implausibly small (blank/player UI)"
                        else:
                            try:
                                from PIL import Image, ImageStat

                                stats = ImageStat.Stat(Image.open(out).convert("L"))
                                if stats.stddev and stats.stddev[0] < 8:
                                    payload["error"] = "screenshot has too little visual variation"
                            except Exception:
                                pass
                        if not payload["error"]:
                            payload.update(
                                {
                                    "status": "succeeded",
                                    "actual_seconds": round(float(actual["t"]), 3),
                                    "duration_seconds": actual.get("duration"),
                                    "video_width": actual.get("width"),
                                    "video_height": actual.get("height"),
                                    "page_title": actual.get("title"),
                                    "output_sha256": sha256_file(out),
                                    "output_bytes": out.stat().st_size,
                                }
                            )
                except Exception as exc:
                    payload["error"] = f"{type(exc).__name__}: {exc}"
                _write_sidecar(sidecar, payload)
                frames.append(payload)
        finally:
            page.close()
            browser.close()
    return frames


def make_contact_sheet(frames: list[dict], out_path: Path, title: str) -> dict:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        raise FrameError("Pillow is required for contact sheets") from exc
    successes = [f for f in frames if f.get("status") == "succeeded" and f.get("output_path")]
    if not successes:
        raise FrameError("no successful frames for contact sheet")
    thumb_w, thumb_h, label_h, pad = 426, 240, 34, 10
    cols = 3
    rows = (len(successes) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (thumb_w + pad) + pad,
                              rows * (thumb_h + label_h + pad) + pad + 42), "white")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        small = ImageFont.truetype("arial.ttf", 13)
    except Exception:
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    draw.text((pad, pad), title, fill="black", font=font)
    y0 = pad + 34
    for index, frame in enumerate(successes):
        path = REPO / frame["output_path"] if not Path(frame["output_path"]).is_absolute() else Path(frame["output_path"])
        try:
            img = Image.open(path).convert("RGB")
        except Exception:
            continue
        img.thumbnail((thumb_w, thumb_h))
        col = index % cols
        row = index // cols
        x = pad + col * (thumb_w + pad)
        y = y0 + row * (thumb_h + label_h + pad)
        sheet.paste(img, (x, y))
        label = (
            f"req {format_timestamp(frame['requested_seconds'])}  "
            f"actual {format_timestamp(frame.get('actual_seconds', 0))}"
        )
        draw.rectangle([x, y + thumb_h, x + thumb_w, y + thumb_h + label_h], fill="white")
        draw.text((x + 2, y + thumb_h + 4), label, fill="black", font=small)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, "JPEG", quality=90)
    return {
        "path": str(out_path.relative_to(REPO)) if out_path.is_relative_to(REPO) else str(out_path),
        "sha256": sha256_file(out_path),
        "bytes": out_path.stat().st_size,
        "frames": [f["output_path"] for f in successes],
        "columns": cols,
    }


def resolve_source(manifest_path: Path, source_id: str) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = next((s for s in manifest.get("sources", []) if s["source_id"] == source_id), None)
    if not source:
        raise FrameError(f"unknown source_id {source_id!r}")
    if not source.get("video_id"):
        raise FrameError(f"source {source_id!r} has no verified video_id")
    return source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-id")
    parser.add_argument("--url")
    parser.add_argument("--local-video")
    parser.add_argument("--timestamps", help="comma-separated HH:MM:SS, MM:SS or seconds")
    parser.add_argument("--timestamp", help="one timestamp (alias)")
    parser.add_argument("--around-seconds", type=float, default=0)
    parser.add_argument("--contact-sheet", action="store_true")
    parser.add_argument("--out-dir", default=str(DEFAULT_CACHE))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--no-reuse", action="store_true")
    args = parser.parse_args(argv)

    raw_times = []
    if args.timestamps:
        raw_times.extend(part for part in args.timestamps.split(",") if part.strip())
    if args.timestamp:
        raw_times.append(args.timestamp)
    if not raw_times:
        parser.error("provide --timestamps or --timestamp")
    try:
        timestamps = [parse_timestamp(value) for value in raw_times]
        plan = build_plan(timestamps, args.around_seconds)
    except FrameError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    source = None
    source_id = None
    video_id = None
    local_video = None
    if args.source_id:
        try:
            source = resolve_source(Path(args.manifest), args.source_id)
        except FrameError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        source_id = args.source_id
        video_id = source["video_id"]
    elif args.url:
        try:
            video_id = extract_video_id(args.url)
        except FrameError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    elif args.local_video:
        local_video = Path(args.local_video)
    else:
        parser.error("provide --source-id, --url or --local-video")

    out_dir = Path(args.out_dir).resolve()
    if not out_dir.is_relative_to(REPO.resolve()) and not args.local_video:
        print("ERROR: --out-dir must be inside the repository", file=sys.stderr)
        return 2
    try:
        if video_id:
            frames = capture_youtube(
                video_id, plan, out_dir, source, source_id, args.headed, not args.no_reuse
            )
        else:
            frames = capture_local(
                local_video, plan, out_dir, source, source_id, not args.no_reuse
            )
    except FrameError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    contact = None
    if args.contact_sheet:
        try:
            tag = safe_component(source_id or video_id or (local_video.stem if local_video else "frames"))
            contact = make_contact_sheet(frames, out_dir / f"{tag}-contact-sheet.jpg",
                                         f"{tag} frame review")
        except FrameError as exc:
            print(f"WARN: contact sheet failed: {exc}", file=sys.stderr)
    index = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_id": source_id,
        "video_id": video_id,
        "video_url": canonical_url(video_id) if video_id else None,
        "requested_timestamps": timestamps,
        "around_seconds": args.around_seconds,
        "method": "playwright-chromium-video-element" if video_id else "ffmpeg-local-frame",
        "frames": frames,
        "contact_sheet": contact,
        "success_count": sum(1 for f in frames if f.get("status") == "succeeded"),
        "failure_count": sum(1 for f in frames if f.get("status") != "succeeded"),
    }
    index_path = out_dir / f"{safe_component(source_id or video_id or local_video.stem)}-capture-index.json"
    _write_sidecar(index_path, index)
    print(json.dumps({k: index[k] for k in ("success_count", "failure_count", "contact_sheet")}, indent=2))
    if index["failure_count"]:
        for frame in frames:
            if frame.get("status") != "succeeded":
                print(f"FAILED {frame.get('capture_seconds')}: {frame.get('error')}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
