from __future__ import annotations

from typing import Optional

from .tool_calling_agent import ToolCallingAgent


class GeneralToolAgent(ToolCallingAgent):
    """
    General-purpose tool-calling agent with pragmatic defaults.
    """

    DEFAULT_PROMPT = (
        "You are a helpful general-purpose agent. Use tools when necessary.\n"
        "- Ask for clarification if requirements are ambiguous.\n"
        "- Prefer accurate, concise results with actionable steps.\n"
        "- Do not reveal internal reasoning. Provide only the final answer.\n"
    )

    def _build_system_prompt(self) -> Optional[str]:
        base = self.config.get("system_prompt")
        prompt = self.DEFAULT_PROMPT
        return f"{prompt}\n{base}" if base else prompt