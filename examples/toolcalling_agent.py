# from __future__ import annotations
# import os

# # Load .env in dev; no-op if missing
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except Exception:
#     pass

# from src.tools import load_builtin_tools, registry
# from src.llm.openrouter_provider import OpenRouterProvider
# from src.agents.llm_tool_agent import LLMToolAgent
# from src.utils.config_loader import load_config, get_openrouter_cfg


# def main():
#     # Ensure built-in tools auto-register
#     load_builtin_tools()

#     # Configure OpenRouter
#     cfg = load_config(["config/default.yaml"])
#     or_cfg = get_openrouter_cfg(cfg)
#     llm = OpenRouterProvider.from_config(or_cfg)

#     # Allow a curated set of tools
#     allowed = ["web.search", "web.scrape", "web.fetch", "web.rss", "system.echo"]

#     agent = LLMToolAgent(
#         name="generalist",
#         config={"max_results": 5},
#         llm=llm,
#         tool_allowlist=allowed,
#         max_steps=6,
#         parallel_tool_calls=True,
#         system_prompt=None,
#     )

#     task = "What's trending today in the stock market? Use tools as needed, and give 3 bullet points with links."
#     result = agent.process_task(task)

#     print("\n=== Final ===")
#     print(result["final"])


# if __name__ == "__main__":
#     if not os.getenv("OPENROUTER_API_KEY"):
#         print("Warning: OPENROUTER_API_KEY not set. Add it to .env or export it.")
#     main()


# 02

# from __future__ import annotations
# import asyncio
# import os
# from typing import Dict, Optional, List

# # Load .env in dev; no-op if missing
# try:
#     from dotenv import load_dotenv
#     load_dotenv()
# except Exception:
#     pass

# from src.tools import load_builtin_tools, registry
# from src.agents.llm_tool_agent import LLMToolAgent
# from src.orchestration.interaction_policy import ToolUsePolicy, AutonomyLevel
# from src.orchestration.tool_call_orchestrator import UIAdapter
# from src.llm.openrouter_provider import OpenRouterProvider
# from src.utils.config_loader import load_config, get_openrouter_cfg


# class CLIAdapter(UIAdapter):
#     async def confirm_tool_call(self, *, tool_name: str, arguments: Dict[str, any], reason: str) -> bool:
#         print(f"\n[Confirm] Tool: {tool_name}\nArgs: {arguments}\nReason: {reason}")
#         ans = input("Proceed? (y/N): ").strip().lower()
#         return ans == "y"

#     async def ask_user(self, *, question: str, options: Optional[List[str]] = None, allow_free_text: bool = True) -> str:
#         print(f"\n[Question] {question}")
#         if options:
#             print("Options:", ", ".join(options))
#         return input("Your answer: ").strip()

#     async def emit_event(self, kind: str, payload: Dict[str, any]) -> None:
#         if kind == "assistant_message" and payload.get("content"):
#             print("\n[Assistant]", payload["content"])
#         elif kind == "tool_call":
#             fn = payload.get("raw", {}).get("function", {})
#             print(f"\n[Tool Call] {fn.get('name')}({fn.get('arguments')})")
#         elif kind == "tool_result":
#             print(f"[Tool Result] {payload.get('tool')} ...")


# def main():
#     load_builtin_tools()

#     cfg = load_config(["config/default.yaml"])
#     or_cfg = get_openrouter_cfg(cfg)
#     llm = OpenRouterProvider.from_config(or_cfg)

#     # Autonomous policy: no confirmations
#     auto_policy = ToolUsePolicy(
#         autonomy=AutonomyLevel.auto,
#         max_steps=6,
#         confirm_tools=set(),
#         deny_tools=set(),
#         allow_tools=None,  # allow all registered by agent
#     )

#     # Confirm policy: confirm all tools
#     confirm_policy = ToolUsePolicy(
#         autonomy=AutonomyLevel.confirm,
#         max_steps=6,
#         confirm_tools=set(),  # empty set here means "confirm all" in our orchestrator logic
#     )

#     ui = CLIAdapter()

#     # Choose one policy
#     policy = auto_policy  # or confirm_policy

#     # Allow a set of tools, including the UI tool for clarifications
#     allowed = ["web.search", "web.scrape", "web.fetch", "system.echo", "ui.ask"]

#     agent = LLMToolAgent(
#         name="generalist",
#         config={"max_steps": 6, "temperature": 0.2},
#         llm=llm,
#         tools=[registry.get_tool(n) for n in allowed if registry.has_tool(n)],
#         policy=policy,
#         ui=ui,
#         system_prompt=None,
#     )

#     task = "What's trending today in the stock market? Ask me if you need preferences, then give 3 bullet points with links."
#     result = agent.process_task(task)

#     print("\n=== Final ===")
#     print(result["final"])


# if __name__ == "__main__":
#     if not os.getenv("OPENROUTER_API_KEY"):
#         print("Warning: OPENROUTER_API_KEY not set. Add it to .env or export it.")
#     main()

from __future__ import annotations
import os
from typing import Dict, Optional, List

# Load .env in dev; no-op if missing
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from src.tools import load_builtin_tools, registry
from src.agents.llm_tool_agent import LLMToolAgent
from src.orchestration.interaction_policy import ToolUsePolicy, AutonomyLevel
from src.orchestration.tool_call_orchestrator import UIAdapter
from src.llm.openrouter_provider import OpenRouterProvider
from src.utils.config_loader import load_config, get_openrouter_cfg


class CLIAdapter(UIAdapter):
    async def confirm_tool_call(self, *, tool_name: str, arguments: Dict[str, any], reason: str) -> bool:
        print(f"\n[Confirm] Tool: {tool_name}\nArgs: {arguments}\nReason: {reason}")
        ans = input("Proceed? (y/N): ").strip().lower()
        return ans == "y"

    async def ask_user(self, *, question: str, options: Optional[List[str]] = None, allow_free_text: bool = True) -> str:
        print(f"\n[Question] {question}")
        if options:
            print("Options:", ", ".join(options))
        return input("Your answer: ").strip()

    async def emit_event(self, kind: str, payload: Dict[str, any]) -> None:
        if kind == "assistant_message" and payload.get("content"):
            print("\n[Assistant]", payload["content"])
        elif kind == "tool_call":
            fn = payload.get("raw", {}).get("function", {})
            print(f"\n[Tool Call] {fn.get('name')}({fn.get('arguments')})")
        elif kind == "tool_result":
            print(f"[Tool Result] {payload.get('tool')} ...")


def main():
    load_builtin_tools()

    cfg = load_config(["config/default.yaml"])
    or_cfg = get_openrouter_cfg(cfg)
    llm = OpenRouterProvider.from_config(or_cfg)

    # Autonomous policy (no prompts). For confirm mode, set autonomy=AutonomyLevel.confirm.
    policy = ToolUsePolicy(
        autonomy=AutonomyLevel.auto,
        max_steps=6,
        # confirm_tools=set(),  # In confirm mode, empty set means confirm all tools
    )

    # Allow a curated set of tools, including the UI tool for clarifications
    allowed = ["web.search", "web.scrape", "web.fetch", "system.echo", "ui.ask"]

    agent = LLMToolAgent(
        name="generalist",
        config={"max_steps": 6, "temperature": 0.2},
        llm=llm,
        tools=[registry.get_tool(n) for n in allowed if registry.has_tool(n)],
        policy=policy,
        ui=CLIAdapter(),
        system_prompt=None,
    )

    task = "What's trending today in the stock market? Ask me if you need preferences, then give 3 bullet points with links."
    result = agent.process_task(task)

    print("\n=== Final ===")
    print(result["final"])


if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY not set. Add it to .env or export it.")
    main()