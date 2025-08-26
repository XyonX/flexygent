from __future__ import annotations

from typing import Any, Iterable, Generator, Optional


class SimpleLLMProvider:
    """
    A minimal LLM provider for local testing and examples.

    - send_message: returns a simple "summary" by truncating and echoing content.
    - stream_message: yields small chunks to simulate streaming.

    Replace this with a real provider (OpenAI, Anthropic, etc.) later, keeping the same interface:
      - send_message(message: str) -> Any
      - stream_message(message: str) -> Iterable[str]
    """

    def __init__(self, max_output_chars: int = 800) -> None:
        self.max_output_chars = max_output_chars

    def send_message(self, message: str) -> str:
        # Extremely naive "summary": keep the first N chars and prepend a label.
        text = message.strip()
        if len(text) > self.max_output_chars:
            text = text[: self.max_output_chars] + "..."
        return f"[SimpleLLM summary]\n{text}"

    def stream_message(self, message: str) -> Generator[str, None, None]:
        # Yield in small chunks to simulate streaming
        full = self.send_message(message)
        chunk_size = 64
        for i in range(0, len(full), chunk_size):
            yield full[i : i + chunk_size]