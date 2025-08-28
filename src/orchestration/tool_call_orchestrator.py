from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional, Protocol, Tuple

from src.tools.registry import registry
from src.tools.base_tool import ToolExecutionError
from src.orchestration.interaction_policy import AutonomyLevel, ToolUsePolicy
from src.llm.openrouter_provider import OpenRouterProvider


def _to_openai_tool_specs(tool_names: List[str]) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    for tname in tool_names:
        tool = registry.get_tool(tname)
        schema = tool.get_schema()
        specs.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["parameters"],
            },
        })
    # Special UI tool spec (virtual tool) for explicit clarifications
    if "ui.ask" in tool_names:
        specs.append({
            "type": "function",
            "function": {
                "name": "ui.ask",
                "description": "Ask the user a question and wait for their response. Use when you need a preference or missing input.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string", "description": "Question to ask the user"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional multiple-choice options"
                        },
                        "allow_free_text": {"type": "boolean", "default": True, "description": "Allow free-text answers"}
                    },
                    "required": ["question"]
                }
            }
        })
    return specs


class UIAdapter(Protocol):
    async def confirm_tool_call(self, *, tool_name: str, arguments: Dict[str, Any], reason: str) -> bool: ...
    async def ask_user(self, *, question: str, options: Optional[List[str]] = None, allow_free_text: bool = True) -> str: ...
    async def emit_event(self, kind: str, payload: Dict[str, Any]) -> None: ...


class NoopUIAdapter:
    async def confirm_tool_call(self, *, tool_name: str, arguments: Dict[str, Any], reason: str) -> bool:
        return True

    async def ask_user(self, *, question: str, options: Optional[List[str]] = None, allow_free_text: bool = True) -> str:
        return ""

    async def emit_event(self, kind: str, payload: Dict[str, Any]) -> None:
        return None


class ToolCallOrchestrator:
    """
    LLM-driven tool-calling loop with optional UI confirmation and user questions.
    """

    def __init__(
        self,
        llm: OpenRouterProvider,
        *,
        policy: Optional[ToolUsePolicy] = None,
        ui: Optional[UIAdapter] = None,
        default_system_prompt: Optional[str] = None,
    ) -> None:
        self.llm = llm
        self.policy = policy or ToolUsePolicy()
        self.ui = ui or NoopUIAdapter()
        self.default_system_prompt = default_system_prompt or (
            "You are FlexyGent. Decide which tools to call and when to stop. "
            "Ask the user via the 'ui.ask' tool if you need preferences or missing inputs."
        )

    async def run(
        self,
        user_message: str,
        *,
        tool_names: List[str],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        tools = self._filter_tools(tool_names)
        messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt or self.default_system_prompt},
                                          {"role": "user", "content": user_message}]
        specs = _to_openai_tool_specs(tools)
        tool_calls_total = 0

        for step in range(self.policy.max_steps):
            await self.ui.emit_event("assistant_loop_step", {"step": step + 1})

            resp = self.llm.chat(messages, tools=specs, tool_choice="auto", temperature=temperature, max_tokens=max_tokens)
            choice = resp["choices"][0]
            msg = choice["message"]
            tool_calls = msg.get("tool_calls") or []
            content = msg.get("content")

            if content:
                await self.ui.emit_event("assistant_message", {"content": content})

            if tool_calls:
                messages.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})
                # Enforce tool call cap
                tool_calls_total += len(tool_calls)
                if self.policy.max_tool_calls is not None and tool_calls_total > self.policy.max_tool_calls:
                    deny_msg = "Tool call limit reached; provide the best answer without more tools."
                    messages.append({"role": "system", "content": deny_msg})
                    continue

                # Execute tools (consider policy and UI)
                tool_result_msgs = await self._execute_tool_calls(tool_calls, allowed=tools, context=context)
                messages.extend(tool_result_msgs)
                # Loop back with tool outputs
                continue

            # No tool calls => final answer
            if content:
                return {
                    "final": content,
                    "messages": messages,
                    "steps": step + 1,
                    "finish_reason": choice.get("finish_reason"),
                }

            # Neither tool_calls nor content – stop
            break

        fallback = "[Tool-calling loop ended without a definitive answer.]"
        return {"final": fallback, "messages": messages, "steps": self.policy.max_steps, "finish_reason": "max_steps"}

    # Internals ----------------------------------------------------------------

    def _filter_tools(self, tool_names: List[str]) -> List[str]:
        if self.policy.autonomy == AutonomyLevel.never:
            return []  # LLM won't be given any tools
        if self.policy.allow_tools is not None:
            allowed = [t for t in tool_names if t in self.policy.allow_tools]
        else:
            allowed = tool_names[:]
        # Keep virtual ui.ask if present in input list
        return allowed

    async def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]], *, allowed: List[str], context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        async def _run_one(tc: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
            await self.ui.emit_event("tool_call", {"raw": tc})
            tc_id = tc.get("id", "")
            fn = tc.get("function", {}) or {}
            name = fn.get("name", "")
            args_raw = fn.get("arguments", "") or "{}"

            # Deny if not allowed
            if name not in allowed:
                result = {"error": f"Tool '{name}' is not allowed by policy."}
                return tc_id, self._tool_message(name, tc_id, result)

            # Parse args
            try:
                args = json.loads(args_raw)
            except Exception as e:
                return tc_id, self._tool_message(name, tc_id, {"error": f"Invalid JSON arguments: {e}", "raw": args_raw})

            # Special virtual tool: ui.ask -> route to UI, await reply, return as result
            if name == "ui.ask":
                question = str(args.get("question", "")).strip()
                options = args.get("options") or None
                allow_free_text = bool(args.get("allow_free_text", True))
                await self.ui.emit_event("ask_user", {"question": question, "options": options})
                answer = await self.ui.ask_user(question=question, options=options, allow_free_text=allow_free_text)
                return tc_id, self._tool_message(name, tc_id, {"answer": answer})

            # Confirm if policy requires
            if self.policy.autonomy == AutonomyLevel.confirm and (name in self.policy.confirm_tools or not self.policy.confirm_tools):
                ok = await self.ui.confirm_tool_call(tool_name=name, arguments=args, reason="policy_confirmation")
                if not ok:
                    return tc_id, self._tool_message(name, tc_id, {"error": "User denied tool call."})

            # Deny-list
            if name in self.policy.deny_tools:
                return tc_id, self._tool_message(name, tc_id, {"error": "Tool is denied by policy."})

            # Execute actual tool
            try:
                tool = registry.get_tool(name)
                out = await tool(args, context=context)
                result = out.model_dump() if hasattr(out, "model_dump") else out
            except ToolExecutionError as te:
                result = {"error": str(te)}
            except Exception as e:
                result = {"error": f"Unexpected tool error: {e!r}"}

            # Truncate
            result_str = json.dumps(result) if not isinstance(result, str) else result
            if self.policy.tool_result_truncate and len(result_str) > self.policy.tool_result_truncate:
                result_str = result_str[: self.policy.tool_result_truncate] + "...[truncated]"

            await self.ui.emit_event("tool_result", {"tool": name, "result_preview": result_str[:400]})
            return tc_id, self._tool_message(name, tc_id, result_str)

        if self.policy.parallel_tool_calls and len(tool_calls) > 1:
            pairs = await asyncio.gather(*[_run_one(tc) for tc in tool_calls])
        else:
            pairs = [await _run_one(tc) for tc in tool_calls]

        id_to_msg = {tc_id: msg for tc_id, msg in pairs}
        ordered = [id_to_msg.get(tc.get("id", "")) for tc in tool_calls]
        return [m for m in ordered if m is not None]

    def _tool_message(self, name: str, tool_call_id: str, content: Any) -> Dict[str, Any]:
        if not isinstance(content, str):
            try:
                content = json.dumps(content)
            except Exception:
                content = str(content)
        return {"role": "tool", "name": name, "tool_call_id": tool_call_id, "content": content}