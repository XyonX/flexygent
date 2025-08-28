import sys
import os
import signal
from typing import Dict, Optional, List

from colorama import Fore, Style, init as colorama_init
from pyfiglet import Figlet

from src.tools import load_builtin_tools, registry
from src.llm.openrouter_provider import OpenRouterProvider
from src.utils.config_loader import load_config, get_openrouter_cfg
from src.agents.llm_tool_agent import LLMToolAgent
from src.orchestration.interaction_policy import ToolUsePolicy, AutonomyLevel
from src.orchestration.tool_call_orchestrator import UIAdapter

# ---- ASCII Banner ----
def print_banner():
    colorama_init(autoreset=True)
    fig = Figlet(font='slant')
    banner = fig.renderText('FlexyGent')
    print(Fore.CYAN + banner + Style.RESET_ALL)
    print(Fore.MAGENTA + "  Your Terminal Agentic AI" + Style.RESET_ALL)
    print(Fore.YELLOW + "-"*60 + Style.RESET_ALL)

# ---- CLI Adapter ----
class TerminalUIAdapter(UIAdapter):
    def __init__(self):
        colorama_init(autoreset=True)

    async def confirm_tool_call(self, *, tool_name: str, arguments: Dict[str, any], reason: str) -> bool:
        print(Fore.YELLOW + f"\n[FlexyGent] Tool '{tool_name}' wants to run with arguments: {arguments}")
        ans = input(Fore.YELLOW + "Allow? (y/N): " + Style.RESET_ALL).strip().lower()
        return ans == "y"

    async def ask_user(self, *, question: str, options: Optional[List[str]] = None, allow_free_text: bool = True) -> str:
        print(Fore.GREEN + f"\n[FlexyGent] {question}")
        if options:
            print(Fore.GREEN + "Options: " + ", ".join(options))
        return input(Fore.GREEN + "Your answer: " + Style.RESET_ALL).strip()

    async def emit_event(self, kind: str, payload: Dict[str, any]) -> None:
        if kind == "assistant_message" and payload.get("content"):
            print(Fore.CYAN + "\nFlexyGent:" + Style.RESET_ALL, payload["content"])
        elif kind == "tool_call":
            fn = payload.get("raw", {}).get("function", {})
            print(Fore.BLUE + f"\n[Tool Call] {fn.get('name')}({fn.get('arguments')})" + Style.RESET_ALL)
        elif kind == "tool_result":
            print(Fore.BLUE + f"[Tool Result] {payload.get('tool')} ..." + Style.RESET_ALL)

# ---- Main CLI Loop ----
def main():
    def handle_exit(sig, frame):
        print(Fore.RED + "\nExiting FlexyGent. Goodbye!" + Style.RESET_ALL)
        sys.exit(0)
    signal.signal(signal.SIGINT, handle_exit)

    print_banner()
    load_builtin_tools()
    cfg = load_config(["config/default.yaml"])
    or_cfg = get_openrouter_cfg(cfg)
    llm = OpenRouterProvider.from_config(or_cfg)

    # Policy: fully autonomous, or confirm tool calls (change as needed)
    policy = ToolUsePolicy(
        autonomy=AutonomyLevel.auto,
        max_steps=6,
    )
    allowed = ["web.search", "web.scrape", "system.echo", "ui.ask"]
    agent = LLMToolAgent(
        name="cli_agent",
        config={"max_steps": 6, "temperature": 0.2},
        llm=llm,
        tools=[registry.get_tool(n) for n in allowed if registry.has_tool(n)],
        policy=policy,
        ui=TerminalUIAdapter(),
        system_prompt=None,
    )

    print(Fore.GREEN + "Type your message (or 'quit' to exit):" + Style.RESET_ALL)
    while True:
        try:
            user = input(Fore.YELLOW + "> " + Style.RESET_ALL).strip()
            if not user:
                continue
            if user.lower() in {"exit", "quit"}:
                print(Fore.RED + "Goodbye!" + Style.RESET_ALL)
                break
            result = agent.process_task(user)
            print(Fore.CYAN + "\n[FlexyGent Final Answer] " + Style.RESET_ALL + result.get("final", ""))
        except EOFError:
            print(Fore.RED + "\nGoodbye!" + Style.RESET_ALL)
            break
        except Exception as e:
            print(Fore.RED + f"\n[Error] {e}" + Style.RESET_ALL)

if __name__ == "__main__":
    main()