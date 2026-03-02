"""Endpoint-aware provider router with cached delegate instances."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from orbitclaw.config.schema import EndpointProviderConfig
from orbitclaw.providers.base import LLMProvider, LLMResponse
from orbitclaw.providers.custom_provider import CustomProvider
from orbitclaw.providers.litellm_provider import LiteLLMProvider
from orbitclaw.providers.registry import find_by_name

_ENDPOINT_TYPE_ALIASES = {
    "openai-compatible": "openai_compatible",
    "openai_compat": "openai_compatible",
    "custom": "openai_compatible",
}

_LITELLM_ENDPOINT_TYPES = {
    "anthropic",
    "openai",
    "openrouter",
    "deepseek",
    "groq",
    "zhipu",
    "dashscope",
    "vllm",
    "gemini",
    "moonshot",
    "minimax",
    "aihubmix",
    "siliconflow",
    "volcengine",
}


class RouterProvider(LLMProvider):
    """Routes `endpoint/model` requests to endpoint-specific cached providers."""

    def __init__(
        self,
        *,
        default_model: str,
        endpoints: Mapping[str, EndpointProviderConfig] | None,
        fallback_factory: Callable[[str], LLMProvider],
    ):
        super().__init__(api_key=None, api_base=None)
        self.default_model = default_model
        self._fallback_factory = fallback_factory
        self._fallback_cache: dict[str, LLMProvider] = {}
        self._endpoints: dict[str, EndpointProviderConfig] = {
            str(name).strip(): cfg
            for name, cfg in (endpoints or {}).items()
            if str(name).strip()
        }
        self._endpoint_cache: dict[str, LLMProvider] = {}

    def _normalize_endpoint_type(self, value: str | None) -> str:
        raw = (value or "openai_compatible").strip().lower()
        raw = _ENDPOINT_TYPE_ALIASES.get(raw, raw)
        return raw

    def _split_endpoint_model(self, model: str | None) -> tuple[str, EndpointProviderConfig, str] | None:
        text = (model or "").strip()
        if "/" not in text:
            return None
        endpoint_name, endpoint_model = text.split("/", 1)
        endpoint_name = endpoint_name.strip()
        endpoint_model = endpoint_model.strip()
        if not endpoint_name or not endpoint_model:
            return None
        cfg = self._endpoints.get(endpoint_name)
        if not cfg or not bool(getattr(cfg, "enabled", True)):
            return None
        return endpoint_name, cfg, endpoint_model

    def _validate_endpoint_model(self, endpoint_name: str, cfg: EndpointProviderConfig, endpoint_model: str) -> tuple[bool, str | None]:
        allowed = [m for m in (cfg.models or []) if str(m).strip()]
        if allowed:
            full_ref = f"{endpoint_name}/{endpoint_model}"
            if endpoint_model not in allowed and full_ref not in allowed:
                return False, f"模型 `{endpoint_model}` 不在 endpoint `{endpoint_name}` 的允许列表中"
        etype = self._normalize_endpoint_type(cfg.type)
        if etype == "openai_compatible":
            return True, f"{endpoint_name} ({etype})"
        if etype in _LITELLM_ENDPOINT_TYPES and find_by_name(etype):
            return True, f"{endpoint_name} ({etype})"
        return False, f"endpoint `{endpoint_name}` 使用了不支持的类型 `{cfg.type}`"

    def _build_endpoint_provider(self, endpoint_name: str, cfg: EndpointProviderConfig, endpoint_model: str) -> LLMProvider:
        etype = self._normalize_endpoint_type(cfg.type)
        if etype == "openai_compatible":
            return CustomProvider(
                api_key=cfg.api_key or "no-key",
                api_base=cfg.api_base or "http://localhost:8000/v1",
                default_model=endpoint_model,
            )
        if etype in _LITELLM_ENDPOINT_TYPES:
            return LiteLLMProvider(
                api_key=cfg.api_key or None,
                api_base=cfg.api_base,
                default_model=endpoint_model,
                extra_headers=cfg.extra_headers or None,
                provider_name=etype,
            )
        raise ValueError(f"Unsupported endpoint type: {cfg.type}")

    def _get_or_create_endpoint_provider(self, endpoint_name: str, cfg: EndpointProviderConfig, endpoint_model: str) -> LLMProvider:
        provider = self._endpoint_cache.get(endpoint_name)
        if provider is None:
            provider = self._build_endpoint_provider(endpoint_name, cfg, endpoint_model)
            self._endpoint_cache[endpoint_name] = provider
        return provider

    def _get_fallback_provider(self, model: str) -> LLMProvider:
        key = model.strip()
        provider = self._fallback_cache.get(key)
        if provider is None:
            provider = self._fallback_factory(key)
            self._fallback_cache[key] = provider
        return provider

    def prepare_model(self, model: str) -> tuple[bool, str | None]:
        parsed = self._split_endpoint_model(model)
        if not parsed:
            # Non-endpoint model path: defer to fallback provider if available.
            try:
                provider = self._get_fallback_provider(model)
            except Exception as e:
                return False, str(e)
            return provider.prepare_model(model)

        endpoint_name, cfg, endpoint_model = parsed
        ok, detail = self._validate_endpoint_model(endpoint_name, cfg, endpoint_model)
        if not ok:
            return False, detail
        try:
            self._get_or_create_endpoint_provider(endpoint_name, cfg, endpoint_model)
        except Exception as e:
            return False, str(e)
        return True, detail

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        active_model = model or self.default_model
        parsed = self._split_endpoint_model(active_model)
        if not parsed:
            return await self._get_fallback_provider(active_model).chat(
                messages=messages,
                tools=tools,
                model=active_model,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        endpoint_name, cfg, endpoint_model = parsed
        ok, detail = self._validate_endpoint_model(endpoint_name, cfg, endpoint_model)
        if not ok:
            return LLMResponse(content=f"Error calling LLM: {detail}", finish_reason="error")
        try:
            provider = self._get_or_create_endpoint_provider(endpoint_name, cfg, endpoint_model)
        except Exception as e:
            return LLMResponse(content=f"Error calling LLM: {e}", finish_reason="error")
        return await provider.chat(
            messages=messages,
            tools=tools,
            model=endpoint_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    def get_default_model(self) -> str:
        return self.default_model

    def list_switchable_endpoints(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for name, cfg in self._endpoints.items():
            if not bool(getattr(cfg, "enabled", True)):
                continue
            out[name] = [str(m) for m in (cfg.models or []) if str(m).strip()]
        return out
