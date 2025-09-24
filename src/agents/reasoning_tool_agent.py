from __future__ import annotations

from typing import Any, Dict, Optional

from .tool_calling_agent import ToolCallingAgent


class ReasoningToolAgent(ToolCallingAgent):
    """
    Tool-calling agent with enhanced planning/reflective behavior.

    Configuration (via self.config):
      - reasoning.mode: "react" | "plan-act" | "plan-act-reflect"
      - reasoning.plan_depth: int (suggested planning steps)
      - reasoning.reflection: bool
      - reasoning.constraints: Optional[str] (extra constraints)
    """

    def _build_system_prompt(self) -> Optional[str]:
        base = self.config.get("system_prompt")
        mode = (self.config.get("reasoning", {}) or {}).get("mode", "react")

        # Keep the final answer free of hidden chain-of-thought. We instruct
        # the model to reason internally but not disclose step-by-step thoughts.
        reasoning_prefix = (
            "You are a capable reasoning agent. Use tools when needed.\n"
            "- Think step-by-step internally, but do not reveal internal thoughts.\n"
            "- Formulate plans before acting if helpful.\n"
            "- Use tool results to refine your answer.\n"
            "- Provide a concise, actionable final answer to the user.\n"
        )

        if mode == "plan-act":
            mode_hint = "- First draft a brief internal plan; then execute actions with tools.\n"
        elif mode == "plan-act-reflect":
            mode_hint = "- Draft an internal plan, act using tools, then briefly self-check internally before finalizing.\n"
        else:  # react
            mode_hint = "- Use a ReAct-style approach: reason briefly internally and call tools as necessary.\n"

        constraints = (self.config.get("reasoning", {}) or {}).get("constraints")
        constraints_hint = f"- Constraints: {constraints}\n" if constraints else ""

        prompt = f"{reasoning_prefix}{mode_hint}{constraints_hint}"
        return f"{prompt}\n{base}" if base else prompt

    def _build_context(self, task: str) -> Dict[str, Any]:
        ctx = super()._build_context(task)
        reasoning = self.config.get("reasoning", {}) or {}
        # Pass hints to the orchestrator if it supports richer control
        ctx.update(
            {
                "reasoning": {
                    "mode": reasoning.get("mode", "react"),
                    "plan_depth": int(reasoning.get("plan_depth", 2)),
                    "reflection": bool(reasoning.get("reflection", True)),
                }
            }
        )
        return ctx