"""LLM-assisted extraction pipeline runner.

Processes transcript chunks through a configurable provider, validates output
against strict schema, quarantines malformed output, and persists job state.
Deterministic steps (validation, job state) are provider-independent.
"""
from __future__ import annotations

import json
import hashlib
from tools.llm_provider import ExtractionRequest, ExtractionResult
from tools.extraction_validator import validate_batch
from tools.extraction_job import (
    JobState, JobStatus
)

# Mock provider for deterministic testing (no API keys needed)
class MockProvider:
    """Deterministic mock provider that returns pre-configured responses."""
    def __init__(self, responses: dict[str, str] | None = None):
        self.responses = responses or {}
        self.call_count = 0

    def complete(self, prompt: str) -> str:
        self.call_count += 1
        # Return a canned response based on prompt hash
        key = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        if key in self.responses:
            return self.responses[key]
        # Default: return a valid observation JSON
        return json.dumps([{
            "record_type": "observation",
            "schema_version": 1,
            "id": "OBS-MOCK-1",
            "version": 1,
            "pilot_id": "pilot-mpl-s18-semantic-v1",
            "category": "commentary",
            "claim": "Mock observation from deterministic extraction.",
            "evidence_type": "transcript_statement",
            "verification_state": "unverified",
            "segment_ids": [],
            "source_ids": [],
            "database_refs": [],
            "visual_refs": [],
            "scope": "mock scope",
            "uncertainty": "mock uncertainty",
            "extraction_version": "mock-v1"
        }])


def run_extraction(source_id: str, chunk_start: int, chunk_end: int,
                   provider=None, prompt_template: str = "",
                   source_lines: list[str] | None = None,
                   valid_series_ids: set[str] | None = None) -> ExtractionResult:
    """Run extraction on a single transcript chunk.

    1. Build prompt from template + chunk text.
    2. Call provider.
    3. Parse JSON response.
    4. Validate each candidate.
    5. Quarantine invalid ones.
    6. Return result with valid observations + errors.
    """
    import time
    start_time = time.time()

    if provider is None:
        provider = MockProvider()

    # Build chunk text
    chunk_text = ""
    if source_lines:
        chunk_text = "\n".join(source_lines[chunk_start:chunk_end])

    prompt = prompt_template.replace("{chunk_text}", chunk_text)
    prompt = prompt.replace("{source_id}", source_id)
    prompt = prompt.replace("{start_line}", str(chunk_start + 1))
    prompt = prompt.replace("{end_line}", str(chunk_end))

    result = ExtractionResult(
        request=ExtractionRequest(
            source_id=source_id,
            chunk_start_line=chunk_start,
            chunk_end_line=chunk_end,
            prompt_template=prompt_template,
        ),
        status="pending",
    )

    try:
        raw = provider.complete(prompt)
        result.raw_response = raw
        result.model_used = getattr(provider, 'config', None)
        result.model_used = result.model_used.model if result.model_used else "mock"

        # Parse JSON
        try:
            candidates = json.loads(raw)
        except json.JSONDecodeError as e:
            result.status = "failed"
            result.errors.append(f"JSON parse error: {e}")
            return result

        if not isinstance(candidates, list):
            candidates = [candidates]

        # Validate
        validations = validate_batch(candidates, source_lines, valid_series_ids)
        for v in validations:
            if v.valid and v.record:
                result.observations.append(v.record)
            else:
                result.errors.extend(v.errors)
                # Quarantine invalid
                for cand in candidates:
                    if cand.get("id") == (v.record.get("id") if v.record else None):
                        pass

        if result.observations and not result.errors:
            result.status = "completed"
        elif result.observations and result.errors:
            result.status = "completed"  # partial success
        elif result.errors:
            result.status = "quarantined"
        else:
            result.status = "completed"

    except Exception as e:
        result.status = "failed"
        result.errors.append(f"Provider error: {e}")

    result.processing_time_seconds = time.time() - start_time
    return result


def run_job(job: JobState, provider=None, prompt_template: str = "",
            source_lines: list[str] | None = None,
            valid_series_ids: set[str] | None = None,
            chunk_size: int = 100) -> JobState:
    """Run extraction for all pending chunks in a job."""
    import time
    for chunk in job.pending_chunks():
        chunk.status = JobStatus.RUNNING.value
        chunk.started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        result = run_extraction(
            source_id=chunk.source_id,
            chunk_start=chunk.start_line,
            chunk_end=chunk.end_line,
            provider=provider,
            prompt_template=prompt_template,
            source_lines=source_lines,
            valid_series_ids=valid_series_ids,
        )

        chunk.status = result.status
        chunk.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        chunk.error_message = "; ".join(result.errors) if result.errors else None
        chunk.observation_ids = [o.get("id") for o in result.observations]
        chunk.model_used = result.model_used
        chunk.schema_version = result.schema_version

        job.updated_at = chunk.completed_at

    return job


# Default prompt template for observation extraction
DEFAULT_PROMPT_TEMPLATE = """You are an evidence extraction assistant for MPL ID S18 esports analysis.

Given the following transcript chunk from source {source_id} (lines {start_line}-{end_line}), extract atomic, falsifiable observations.

Rules:
- Each observation must cite exact source line spans.
- Do not invent timestamps; use only provided alignment data.
- Do not invent player/hero/team names not in the source.
- Output valid JSON array of observation objects matching the schema.
- If no observations can be extracted, return an empty array [].

Transcript chunk:
{chunk_text}

Output JSON:"""