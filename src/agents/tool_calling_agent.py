from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, LLMProvider, MemoryStore
from ..tools.base_tool import BaseTool
from ..tools.registry import registry
from ..orchestration.tool_call_orchestrator import ToolCallOrchestrator, UIAdapter
from ..orchestration.interaction_policy import ToolUsePolicy, AutonomyLevel


class ToolCallingAgent(BaseAgent):
    """
    Concrete agent that enables multi-step tool use via a ToolCallOrchestrator.
    Serves as the base class for more capable agents (reasoning, adaptive, general).

    Key features:
    - Uses ToolCallOrchestrator to manage LLM + tool-calling loops.
    - Accepts tool allowlisting or defaults to all registered tools.
    - Supports UI callbacks and policy configuration (autonomy level, max steps).
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        llm: Optional[LLMProvider] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[MemoryStore] = None,
        *,
        policy: Optional[ToolUsePolicy] = None,
        ui: Optional[UIAdapter] = None,
        system_prompt: Optional[str] = None,
        tool_allowlist: Optional[List[str]] = None,
    ) -> None:
        super().__init__(name=name, config=config, llm=llm, tools=tools, memory=memory)

        # Resolve tools/tool names
        if tools is not None:
            resolved_tool_names = [t.name for t in tools]
        elif tool_allowlist:
            resolved_tool_names = [n for n in tool_allowlist if registry.has_tool(n)]
        else:
            # Default to all registered tools (consider restricting in production)
            resolved_tool_names = registry.list_tool_names()

        self._tool_names = resolved_tool_names
        self._system_prompt = system_prompt

        # Construct a default policy from config if not provided
        default_policy = ToolUsePolicy(
            autonomy=AutonomyLevel.auto,
            max_steps=int(config.get("max_steps", 6)),
        )
        self._orchestrator = ToolCallOrchestrator(
            llm=self.llm,  # type: ignore[arg-type]
            policy=policy or default_policy,
            ui=ui,
            default_system_prompt=self._system_prompt,
        )

    def process_task(self, task: str) -> Any:
        return self._run_sync(self._process_task_async(task))

    async def _process_task_async(self, task: str) -> Dict[str, Any]:
        # Allow subclasses to modify the system prompt or context
        system_prompt = self._build_system_prompt()
        context = self._build_context(task)

        res = await self._orchestrator.run(
            task,
            tool_names=self._tool_names,
            system_prompt=system_prompt,
            temperature=float(self.config.get("temperature", 0.2)),
            max_tokens=self.config.get("max_tokens"),
            context=context,
        )

        # Let subclasses react to completion (e.g., adaptation)
        try:
            self.on_task_complete(task=task, result=res)
        except Exception:
            # Do not break the flow on adaptation errors
            pass

        self.update_memory("last_dialog", {"task": task, "messages": res.get("messages")})
        return {"agent": self.name, **res}

    def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        tool = next((t for t in self.tools if t.name == tool_name), registry.get_tool(tool_name))
        return self._run_sync(tool(payload))

    # Extension points for derived classes -------------------------------------

    def _build_system_prompt(self) -> Optional[str]:
        """Subclasses can override to inject behavior-specific system prompts."""
        return self._system_prompt

    def _build_context(self, task: str) -> Dict[str, Any]:
        """Subclasses can override to pass additional context to the orchestrator."""
        return {"agent": self.name}

    def on_task_complete(self, task: str, result: Dict[str, Any]) -> None:
        """Hook for subclasses to learn/adapt/log after each task."""
        return

    # --------------------------------------------------------------------------

    def _run_sync(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        return loop.run_until_complete(coro)


# Backward compatibility alias
class LLMToolAgent(ToolCallingAgent):
    """
    Deprecated alias. Prefer using ToolCallingAgent or a specialized subclass
    (ReasoningToolAgent, AdaptiveToolAgent, GeneralToolAgent).
    """
    pass