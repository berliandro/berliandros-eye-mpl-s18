"""Idempotent extraction job state management.

Tracks processing state by source/chunk. Make retries idempotent, record
model/prompt/schema versions, and allow resuming only failed or changed chunks.
"""
from __future__ import annotations

import json
import os
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    SKIPPED = "skipped"


@dataclass
class ChunkState:
    chunk_id: str
    source_id: str
    start_line: int
    end_line: int
    status: str = JobStatus.PENDING.value
    model_used: Optional[str] = None
    prompt_version: Optional[str] = None
    schema_version: int = 1
    source_hash: Optional[str] = None
    alignment_hash: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    observation_ids: list[str] = field(default_factory=list)
    retry_count: int = 0


@dataclass
class JobState:
    job_id: str
    created_at: str
    updated_at: str
    chunks: dict[str, ChunkState] = field(default_factory=dict)

    def add_chunk(self, chunk: ChunkState) -> None:
        self.chunks[chunk.chunk_id] = chunk
        self.updated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def get_chunk(self, chunk_id: str) -> Optional[ChunkState]:
        return self.chunks.get(chunk_id)

    def pending_chunks(self) -> list[ChunkState]:
        return [c for c in self.chunks.values() if c.status in (JobStatus.PENDING.value, JobStatus.FAILED.value)]

    def completed_chunks(self) -> list[ChunkState]:
        return [c for c in self.chunks.values() if c.status == JobStatus.COMPLETED.value]

    def failed_chunks(self) -> list[ChunkState]:
        return [c for c in self.chunks.values() if c.status == JobStatus.FAILED.value]

    def quarantined_chunks(self) -> list[ChunkState]:
        return [c for c in self.chunks.values() if c.status == JobStatus.QUARANTINED.value]

    def summary(self) -> dict:
        statuses = {}
        for c in self.chunks.values():
            statuses[c.status] = statuses.get(c.status, 0) + 1
        return {
            "job_id": self.job_id,
            "total_chunks": len(self.chunks),
            "statuses": statuses,
            "pending": len(self.pending_chunks()),
            "completed": len(self.completed_chunks()),
            "failed": len(self.failed_chunks()),
            "quarantined": len(self.quarantined_chunks()),
        }

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "chunks": {k: asdict(v) for k, v in self.chunks.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "JobState":
        job = cls(
            job_id=data["job_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
        for k, v in data.get("chunks", {}).items():
            job.chunks[k] = ChunkState(**v)
        return job


def create_job(job_id: str) -> JobState:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return JobState(job_id=job_id, created_at=now, updated_at=now)


def save_job(state: JobState, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)


def load_job(path: str) -> JobState:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return JobState.from_dict(data)


def compute_chunk_id(source_id: str, start_line: int, end_line: int) -> str:
    """Deterministic chunk ID from source and line range."""
    raw = f"{source_id}:{start_line}:{end_line}"
    return "CHUNK-" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def should_process(chunk: ChunkState, current_source_hash: str,
                   current_alignment_hash: str, current_model: str,
                   current_prompt_version: str, current_schema_version: int) -> bool:
    """Determine if a chunk needs (re)processing."""
    if chunk.status in (JobStatus.PENDING.value, JobStatus.FAILED.value):
        return True
    if chunk.status == JobStatus.COMPLETED.value:
        # Re-process if inputs changed
        if chunk.source_hash != current_source_hash:
            return True
        if chunk.alignment_hash != current_alignment_hash:
            return True
        if chunk.model_used != current_model:
            return True
        if chunk.prompt_version != current_prompt_version:
            return True
        if chunk.schema_version != current_schema_version:
            return True
    return False