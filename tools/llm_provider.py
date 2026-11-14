"""Configurable LLM provider adapter for the semantic extraction pipeline.

Keeps model configuration, prompts, schemas and validation separate from
provider transport. Does not hardcode API keys or secrets.
"""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProviderConfig:
    """Configuration for an LLM provider."""
    provider: str  # "openai", "anthropic", "deepseek", "local"
    model: str
    api_key_env: str  # environment variable name, never the key itself
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096
    timeout_seconds: int = 120
    retry_count: int = 3
    retry_delay_seconds: float = 2.0


@dataclass
class ExtractionRequest:
    """A bounded extraction request for one transcript chunk."""
    source_id: str
    chunk_start_line: int
    chunk_end_line: int
    prompt_template: str
    schema_version: int = 1
    model_config: Optional[ProviderConfig] = None


@dataclass
class ExtractionResult:
    """Result of an extraction attempt."""
    request: ExtractionRequest
    status: str  # "completed", "failed", "quarantined", "pending"
    observations: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    model_used: Optional[str] = None
    prompt_version: Optional[str] = None
    schema_version: int = 1
    processing_time_seconds: float = 0.0
    raw_response: Optional[str] = None


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Send a prompt and return the raw text response."""
        ...

    def get_api_key(self) -> Optional[str]:
        """Retrieve API key from environment. Never store it."""
        return os.environ.get(self.config.api_key_env)


class OpenAIProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        # Scaffold: real implementation would use openai SDK
        raise NotImplementedError("OpenAI provider not yet implemented. Set OPENAI_API_KEY.")


class AnthropicProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        raise NotImplementedError("Anthropic provider not yet implemented. Set ANTHROPIC_API_KEY.")


class DeepSeekProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        raise NotImplementedError("DeepSeek provider not yet implemented. Set DEEPSEEK_API_KEY.")


class LocalProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        raise NotImplementedError("Local provider not yet implemented.")


PROVIDER_REGISTRY = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "deepseek": DeepSeekProvider,
    "local": LocalProvider,
}


def create_provider(config: ProviderConfig) -> LLMProvider:
    """Factory: create a provider from config."""
    cls = PROVIDER_REGISTRY.get(config.provider)
    if cls is None:
        raise ValueError(f"Unknown provider: {config.provider}")
    return cls(config)


def load_provider_config(path: str) -> ProviderConfig:
    """Load provider config from a JSON file."""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return ProviderConfig(**data)