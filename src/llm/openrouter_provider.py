# from __future__ import annotations

# import os
# from typing import Any, Dict, Iterable, List, Optional

# from openai import OpenAI
# from openai.types.chat import ChatCompletionMessageParam


# class OpenRouterProvider:
#     """
#     LLMProvider-compatible wrapper for OpenRouter's OpenAI-compatible Chat Completions API.

#     Configuration precedence (highest to lowest):
#       1) Explicit constructor arguments
#       2) Environment variables (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OR_APP_URL, OR_APP_NAME)
#       3) Values provided via from_config(config_dict)

#     Defaults:
#       - base_url: https://openrouter.ai/api/v1
#       - model: qwen/qwen3-coder:free
#     """

#     def __init__(
#         self,
#         *,
#         api_key: Optional[str] = None,
#         base_url: Optional[str] = None,
#         model: str = "qwen/qwen3-coder:free",
#         system_prompt: Optional[str] = None,
#         temperature: float = 0.2,
#         max_tokens: Optional[int] = None,
#         request_timeout: float = 60.0,
#         extra_headers: Optional[Dict[str, str]] = None,
#     ) -> None:
#         # Env overrides (if constructor arg not provided)
#         api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
#         base_url = base_url or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
#         if not api_key:
#             raise RuntimeError("OPENROUTER_API_KEY is not set (and no api_key was provided).")

#         self.client = OpenAI(base_url=base_url, api_key=api_key)
#         self.model = model
#         self.system_prompt = system_prompt
#         self.temperature = temperature
#         self.max_tokens = max_tokens
#         self.request_timeout = request_timeout

#         # Attribution headers (OpenRouter recommendation)
#         self.extra_headers = extra_headers or {
#             "HTTP-Referer": os.environ.get("OR_APP_URL", ""),
#             "X-Title": os.environ.get("OR_APP_NAME", "FlexyGent"),
#         }

#     @classmethod
#     def from_config(cls, cfg: Dict[str, object]) -> "OpenRouterProvider":
#         """
#         Build provider from a config dict (e.g., loaded from YAML).
#         """
#         api_key_env = str(cfg.get("api_key_env") or "OPENROUTER_API_KEY")
#         api_key = (
#             os.environ.get(api_key_env)
#             or os.environ.get("OPENROUTER_API_KEY")
#             or (cfg.get("api_key") or None)  # type: ignore
#         )

#         base_url = str(os.environ.get("OPENROUTER_BASE_URL") or (cfg.get("base_url") or "https://openrouter.ai/api/v1"))
#         model = str(cfg.get("model") or "qwen/qwen3-coder:free")
#         system_prompt = cfg.get("system_prompt") if isinstance(cfg.get("system_prompt"), str) else None  # type: ignore
#         temperature = float(cfg.get("temperature") or 0.2)

#         max_tokens_val = cfg.get("max_tokens")
#         max_tokens = int(max_tokens_val) if max_tokens_val is not None else None

#         request_timeout_val = cfg.get("request_timeout")
#         request_timeout = float(request_timeout_val) if request_timeout_val is not None else 60.0

#         headers = cfg.get("headers") or {}  # type: ignore
#         extra_headers = {
#             "HTTP-Referer": os.environ.get("OR_APP_URL", ""),
#             "X-Title": os.environ.get("OR_APP_NAME", "FlexyGent"),
#             **({k: str(v) for k, v in headers.items()} if isinstance(headers, dict) else {}),
#         }

#         return cls(
#             api_key=api_key,
#             base_url=base_url,
#             model=model,
#             system_prompt=system_prompt,
#             temperature=temperature,
#             max_tokens=max_tokens,
#             request_timeout=request_timeout,
#             extra_headers=extra_headers,
#         )

#     # Simple string API (backwards compatible)
#     def send_message(self, message: str) -> str:
#         messages: List[ChatCompletionMessageParam] = []
#         if self.system_prompt:
#             messages.append({"role": "system", "content": self.system_prompt})
#         messages.append({"role": "user", "content": message})

#         resp = self.client.chat.completions.create(
#             model=self.model,
#             messages=messages,
#             temperature=self.temperature,
#             max_tokens=self.max_tokens,
#             timeout=self.request_timeout,
#             stream=False,
#             extra_headers=self.extra_headers,
#         )
#         return resp.choices[0].message.content or ""

#     def stream_message(self, message: str) -> Iterable[str]:
#         messages: List[ChatCompletionMessageParam] = []
#         if self.system_prompt:
#             messages.append({"role": "system", "content": self.system_prompt})
#         messages.append({"role": "user", "content": message})

#         stream = self.client.chat.completions.create(
#             model=self.model,
#             messages=messages,
#             temperature=self.temperature,
#             max_tokens=self.max_tokens,
#             timeout=self.request_timeout,
#             stream=True,
#             extra_headers=self.extra_headers,
#         )
#         for chunk in stream:
#             if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
#                 yield chunk.choices[0].delta.content

#     # Chat + tool calling API
#     def chat(
#         self,
#         messages: List[Dict[str, Any]],
#         *,
#         tools: Optional[List[Dict[str, Any]]] = None,
#         tool_choice: Optional[Any] = None,
#         temperature: Optional[float] = None,
#         max_tokens: Optional[int] = None,
#         extra_headers: Optional[Dict[str, str]] = None,
#         timeout: Optional[float] = None,
#     ) -> Dict[str, Any]:
#         resp = self.client.chat.completions.create(
#             model=self.model,
#             messages=messages,
#             tools=tools,
#             tool_choice=tool_choice,
#             temperature=temperature if temperature is not None else self.temperature,
#             max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
#             timeout=timeout if timeout is not None else self.request_timeout,
#             stream=False,
#             extra_headers={**self.extra_headers, **(extra_headers or {})},
#         )
#         return resp.model_dump()

#     def stream_chat(
#         self,
#         messages: List[Dict[str, Any]],
#         *,
#         tools: Optional[List[Dict[str, Any]]] = None,
#         tool_choice: Optional[Any] = None,
#         temperature: Optional[float] = None,
#         max_tokens: Optional[int] = None,
#         extra_headers: Optional[Dict[str, str]] = None,
#         timeout: Optional[float] = None,
#     ) -> Iterable[Any]:
#         stream = self.client.chat.completions.create(
#             model=self.model,
#             messages=messages,
#             tools=tools,
#             tool_choice=tool_choice,
#             temperature=temperature if temperature is not None else self.temperature,
#             max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
#             timeout=timeout if timeout is not None else self.request_timeout,
#             stream=True,
#             extra_headers={**self.extra_headers, **(extra_headers or {})},
#         )
#         for chunk in stream:
#             yield chunk

from __future__ import annotations

import os
from typing import Any, Dict, Iterable, List, Optional

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class OpenRouterProvider:
    """
    LLMProvider-compatible wrapper for OpenRouter's OpenAI-compatible Chat Completions API.

    Configuration precedence (highest to lowest):
      1) Explicit constructor arguments
      2) Environment variables (OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OR_APP_URL, OR_APP_NAME)
      3) Values provided via from_config(config_dict)

    Defaults:
      - base_url: https://openrouter.ai/api/v1
      - model: qwen/qwen3-coder:free
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "qwen/qwen3-coder:free",
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        request_timeout: float = 60.0,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        # Env overrides (if constructor arg not provided)
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        base_url = base_url or os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set (and no api_key was provided).")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.request_timeout = request_timeout

        # Attribution headers (OpenRouter recommendation)
        self.extra_headers = extra_headers or {
            "HTTP-Referer": os.environ.get("OR_APP_URL", ""),
            "X-Title": os.environ.get("OR_APP_NAME", "FlexyGent"),
        }

    @classmethod
    def from_config(cls, cfg: Dict[str, object]) -> "OpenRouterProvider":
        """
        Build provider from a config dict (e.g., loaded from YAML).

        Supported keys under cfg:
          - api_key (NOT recommended in files) or api_key_env (env var name holding the key; default OPENROUTER_API_KEY)
          - base_url
          - model
          - system_prompt
          - temperature
          - max_tokens
          - request_timeout
          - headers: { HTTP-Referer, X-Title }
        """
        api_key_env = str(cfg.get("api_key_env") or "OPENROUTER_API_KEY")
        # Precedence: env first, then cfg["api_key"] as fallback
        api_key = os.environ.get(api_key_env) or os.environ.get("OPENROUTER_API_KEY") or (cfg.get("api_key") or None)  # type: ignore

        base_url = str(
            os.environ.get("OPENROUTER_BASE_URL")
            or (cfg.get("base_url") or "https://openrouter.ai/api/v1")
        )
        model = str(cfg.get("model") or "qwen/qwen3-coder:free")
        system_prompt = cfg.get("system_prompt") if isinstance(cfg.get("system_prompt"), str) else None  # type: ignore
        temperature = float(cfg.get("temperature") or 0.2)

        max_tokens_val = cfg.get("max_tokens")
        max_tokens = int(max_tokens_val) if max_tokens_val is not None else None

        request_timeout_val = cfg.get("request_timeout")
        request_timeout = float(request_timeout_val) if request_timeout_val is not None else 60.0

        headers = cfg.get("headers") or {}  # type: ignore
        extra_headers = {
            "HTTP-Referer": os.environ.get("OR_APP_URL", ""),
            "X-Title": os.environ.get("OR_APP_NAME", "FlexyGent"),
            **({k: str(v) for k, v in headers.items()} if isinstance(headers, dict) else {}),
        }

        return cls(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            request_timeout=request_timeout,
            extra_headers=extra_headers,
        )

    # Simple string API (backwards compatible)
    def send_message(self, message: str) -> str:
        messages: List[ChatCompletionMessageParam] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": message})

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.request_timeout,
            stream=False,
            extra_headers=self.extra_headers,
        )
        return resp.choices[0].message.content or ""

    def stream_message(self, message: str) -> Iterable[str]:
        messages: List[ChatCompletionMessageParam] = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": message})

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.request_timeout,
            stream=True,
            extra_headers=self.extra_headers,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    # Chat + tool calling API
    def chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Any] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            timeout=timeout if timeout is not None else self.request_timeout,
            stream=False,
            extra_headers={**self.extra_headers, **(extra_headers or {})},
        )
        return resp.model_dump()

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        *,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Any] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Iterable[Any]:
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            timeout=timeout if timeout is not None else self.request_timeout,
            stream=True,
            extra_headers={**self.extra_headers, **(extra_headers or {})},
        )
        for chunk in stream:
            yield chunk