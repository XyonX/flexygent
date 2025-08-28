# from __future__ import annotations

# import asyncio
# import json
# from typing import Any, Dict, List, Optional, Tuple

# from .base_agent import BaseAgent, LLMProvider, MemoryStore
# from ..tools.base_tool import BaseTool, ToolExecutionError
# from ..tools.registry import registry


# def _to_openai_tool_specs(tool_names: List[str]) -> List[Dict[str, Any]]:
#     """
#     Convert registered tools to OpenAI 'tools' specs:
#       {"type": "function", "function": {"name", "description", "parameters"}}
#     """
#     specs: List[Dict[str, Any]] = []
#     for name in tool_names:
#         tool = registry.get_tool(name)
#         schema = tool.get_schema()
#         specs.append(
#             {
#                 "type": "function",
#                 "function": {
#                     "name": schema["name"],
#                     "description": schema["description"],
#                     "parameters": schema["parameters"],
#                 },
#             }
#         )
#     return specs


# class LLMToolAgent(BaseAgent):
#     """
#     Agent that lets the LLM decide which tools to call in multiple steps.

#     - You provide an allowlist of tool names via tools or tool_allowlist.
#     - The agent sends those tool schemas to the LLM and runs a tool-calling loop.
#     - Each LLM tool_call is executed and fed back as a 'tool' message until the LLM returns a final answer.
#     """

#     def __init__(
#         self,
#         name: str,
#         config: Dict[str, Any],
#         llm: Optional[LLMProvider] = None,
#         tools: Optional[List[BaseTool]] = None,
#         memory: Optional[MemoryStore] = None,
#         *,
#         tool_allowlist: Optional[List[str]] = None,
#         max_steps: int = 8,
#         parallel_tool_calls: bool = True,
#         tool_result_truncate: int = 8000,
#         system_prompt: Optional[str] = None,
#     ) -> None:
#         super().__init__(name=name, config=config, llm=llm, tools=tools, memory=memory)

#         # Build tool set
#         if tool_allowlist:
#             self.tools = [registry.get_tool(n) for n in tool_allowlist if registry.has_tool(n)]
#         elif not self.tools:
#             # fallback to all registered tools (you may want to restrict this)
#             self.tools = registry.list_tools()

#         self._tool_by_name: Dict[str, BaseTool] = {t.name: t for t in self.tools}

#         self.max_steps = int(max_steps)
#         self.parallel_tool_calls = bool(parallel_tool_calls)
#         self.tool_result_truncate = int(tool_result_truncate)
#         self._system_prompt = system_prompt or (
#             "You are FlexyGent. You may call tools to complete the task.\n"
#             "- Use the available tools when needed by emitting tool calls with valid JSON arguments.\n"
#             "- Think step-by-step. Make multiple tool calls if necessary.\n"
#             "- Stop calling tools when you can provide a complete answer."
#         )

#     # Public API ---------------------------------------------------------------

#     def process_task(self, task: str) -> Any:
#         """
#         Sync entrypoint to run the multi-step tool-calling loop.
#         """
#         return self._run_sync(self._process_task_async(task))

#     async def _process_task_async(self, task: str) -> Dict[str, Any]:
#         if not hasattr(self.llm, "chat"):
#             raise RuntimeError(
#                 "The configured LLM provider does not support chat/tool-calling. "
#                 "Use OpenRouterProvider (with chat()) or implement ChatLLMProvider."
#             )

#         messages: List[Dict[str, Any]] = [
#             {"role": "system", "content": self._system_prompt},
#             {"role": "user", "content": task},
#         ]
#         tool_names = [t.name for t in self.tools]
#         tools_param = _to_openai_tool_specs(tool_names)

#         for step in range(self.max_steps):
#             resp = self.llm.chat(messages, tools=tools_param, tool_choice="auto")  # type: ignore[attr-defined]
#             choice = resp["choices"][0]
#             msg = choice["message"]
#             tool_calls = msg.get("tool_calls") or []
#             content = msg.get("content")

#             if tool_calls:
#                 # Record the assistant message containing tool calls
#                 messages.append({"role": "assistant", "content": content or "", "tool_calls": tool_calls})
#                 # Execute tools and append their results
#                 tool_results_msgs = await self._execute_tool_calls(tool_calls)
#                 messages.extend(tool_results_msgs)
#                 continue

#             # Final answer (no tool calls)
#             if content:
#                 messages.append({"role": "assistant", "content": content})
#                 self.update_memory("last_dialog", {"task": task, "messages": messages})
#                 return {
#                     "agent": self.name,
#                     "final": content,
#                     "steps": step + 1,
#                     "messages": messages,
#                     "finish_reason": choice.get("finish_reason"),
#                 }

#             # Neither content nor tool_calls - break
#             break

#         # Step limit reached or no definitive answer
#         fallback = "[No definitive answer after tool-calling loop.]"
#         messages.append({"role": "assistant", "content": fallback})
#         return {"agent": self.name, "final": fallback, "steps": self.max_steps, "messages": messages, "finish_reason": "max_steps"}

#     def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
#         """
#         Direct execution path if you want to call a tool by name outside the loop.
#         """
#         tool = self._require_tool(tool_name)
#         return self._run_sync(tool(payload))

#     # Internal helpers ---------------------------------------------------------

#     async def _execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         async def _run_one(tc: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
#             tc_id = tc.get("id", "")
#             fn = tc.get("function", {}) or {}
#             name = fn.get("name", "")
#             args_raw = fn.get("arguments", "") or "{}"

#             # Parse arguments
#             try:
#                 args = json.loads(args_raw)
#             except Exception as e:
#                 result = {"error": f"Invalid JSON arguments for tool '{name}': {e}", "raw_arguments": args_raw}
#                 return tc_id, self._tool_message(name, tc_id, result)

#             # Execute tool
#             try:
#                 tool = self._require_tool(name)
#                 out = await tool(args, context={"agent": self.name})
#                 result = out.model_dump() if hasattr(out, "model_dump") else out  # pydantic BaseModel to dict
#             except ToolExecutionError as te:
#                 result = {"error": str(te)}
#             except Exception as e:
#                 result = {"error": f"Unexpected error in tool '{name}': {e!r}"}

#             # Truncate
#             result_str = json.dumps(result) if not isinstance(result, str) else result
#             if self.tool_result_truncate and len(result_str) > self.tool_result_truncate:
#                 result_str = result_str[: self.tool_result_truncate] + "...[truncated]"
#             return tc_id, self._tool_message(name, tc_id, result_str)

#         if self.parallel_tool_calls and len(tool_calls) > 1:
#             pairs = await asyncio.gather(*[_run_one(tc) for tc in tool_calls])
#         else:
#             pairs = [await _run_one(tc) for tc in tool_calls]

#         # Preserve original order
#         id_to_msg = {tc_id: msg for tc_id, msg in pairs}
#         ordered = [id_to_msg.get(tc.get("id", "")) for tc in tool_calls]
#         return [m for m in ordered if m is not None]

#     def _tool_message(self, name: str, tool_call_id: str, content: Any) -> Dict[str, Any]:
#         if not isinstance(content, str):
#             try:
#                 content = json.dumps(content)
#             except Exception:
#                 content = str(content)
#         return {"role": "tool", "name": name, "tool_call_id": tool_call_id, "content": content}

#     def _require_tool(self, name: str) -> BaseTool:
#         tool = self._tool_by_name.get(name)
#         if tool is None:
#             if registry.has_tool(name):
#                 tool = registry.get_tool(name)
#                 self._tool_by_name[name] = tool
#             else:
#                 raise ValueError(f"Tool '{name}' not available to agent '{self.name}'.")
#         return tool

#     def _run_sync(self, coro):
#         try:
#             loop = asyncio.get_running_loop()
#         except RuntimeError:
#             return asyncio.run(coro)
#         return loop.run_until_complete(coro)

# 02

# from __future__ import annotations

# from typing import Dict, Optional

# import httpx
# from pydantic import BaseModel, Field

# from ..base_tool import BaseTool
# from ..registry import registry


# class FetchInput(BaseModel):
#     url: str = Field(..., description="URL to fetch via HTTP GET")
#     timeout_ms: int = Field(8000, ge=500, le=60000, description="Timeout in milliseconds")
#     max_bytes: int = Field(500_000, ge=1024, le=5_000_000, description="Maximum response bytes to retain")
#     headers: Optional[Dict[str, str]] = Field(None, description="Optional request headers")
#     decode: bool = Field(True, description="Decode response as text if true")


# class FetchOutput(BaseModel):
#     status_code: int = Field(..., description="HTTP status code")
#     content_type: Optional[str] = Field(None, description="Content-Type header")
#     body: str = Field(..., description="Response body (possibly truncated)")
#     truncated: bool = Field(False, description="Whether the body was truncated")


# class FetchTool(BaseTool[FetchInput, FetchOutput]):
#     name = "web.fetch"
#     description = "Fetch a URL with HTTP GET, returning text body and metadata."
#     input_model = FetchInput
#     output_model = FetchOutput

#     requires_network = True
#     timeout_seconds = 15.0
#     max_concurrency = 8
#     tags = frozenset({"web", "http", "fetch"})

#     async def execute(self, params: FetchInput, *, context: Optional[dict] = None) -> FetchOutput:
#         timeout = httpx.Timeout(params.timeout_ms / 1000.0)
#         async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=params.headers or {}) as client:
#             resp = await client.get(params.url)
#             raw = resp.content
#             truncated = False
#             if len(raw) > params.max_bytes:
#                 raw = raw[: params.max_bytes]
#                 truncated = True
#             if params.decode:
#                 try:
#                     body = raw.decode(resp.encoding or "utf-8", errors="replace")
#                 except Exception:
#                     body = raw.decode("utf-8", errors="replace")
#             else:
#                 body = raw.decode("utf-8", errors="replace")
#             return FetchOutput(
#                 status_code=resp.status_code,
#                 content_type=resp.headers.get("Content-Type"),
#                 body=body,
#                 truncated=truncated,
#             )


# registry.register_tool(FetchTool())\

from __future__ import annotations

from typing import Dict, Optional

import httpx
from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry


class FetchInput(BaseModel):
    url: str = Field(..., description="URL to fetch via HTTP GET")
    timeout_ms: int = Field(8000, ge=500, le=60000, description="Timeout in milliseconds")
    max_bytes: int = Field(500_000, ge=1024, le=5_000_000, description="Maximum response bytes to retain")
    headers: Optional[Dict[str, str]] = Field(None, description="Optional request headers")
    decode: bool = Field(True, description="Decode response as text if true")


class FetchOutput(BaseModel):
    status_code: int = Field(..., description="HTTP status code")
    content_type: Optional[str] = Field(None, description="Content-Type header")
    body: str = Field(..., description="Response body (possibly truncated)")
    truncated: bool = Field(False, description="Whether the body was truncated")


class FetchTool(BaseTool[FetchInput, FetchOutput]):
    name = "web.fetch"
    description = "Fetch a URL with HTTP GET, returning text body and metadata."
    input_model = FetchInput
    output_model = FetchOutput

    requires_network = True
    requires_filesystem = False
    timeout_seconds = 15.0
    max_concurrency = 8
    tags = frozenset({"web", "http", "fetch"})

    async def execute(self, params: FetchInput, *, context: Optional[dict] = None) -> FetchOutput:
        timeout = httpx.Timeout(params.timeout_ms / 1000.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=params.headers or {}) as client:
            resp = await client.get(params.url)
            raw = resp.content
            truncated = False
            if len(raw) > params.max_bytes:
                raw = raw[: params.max_bytes]
                truncated = True
            if params.decode:
                try:
                    body = raw.decode(resp.encoding or "utf-8", errors="replace")
                except Exception:
                    body = raw.decode("utf-8", errors="replace")
            else:
                body = raw.decode("utf-8", errors="replace")
            return FetchOutput(
                status_code=resp.status_code,
                content_type=resp.headers.get("Content-Type"),
                body=body,
                truncated=truncated,
            )


# Auto-register
registry.register_tool(FetchTool())