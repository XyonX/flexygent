from __future__ import annotations
import os

# Load .env in dev; no-op if missing
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from src.tools import load_builtin_tools, registry
from src.llm.openrouter_provider import OpenRouterProvider
from src.agents.llm_tool_agent import LLMToolAgent
from src.utils.config_loader import load_config, get_openrouter_cfg


def main():
    # Ensure built-in tools auto-register
    load_builtin_tools()

    # Configure OpenRouter
    cfg = load_config(["config/default.yaml"])
    or_cfg = get_openrouter_cfg(cfg)
    llm = OpenRouterProvider.from_config(or_cfg)

    # Allow a curated set of tools
    allowed = ["web.search", "web.scrape", "web.fetch", "web.rss", "system.echo"]

    agent = LLMToolAgent(
        name="generalist",
        config={"max_results": 5},
        llm=llm,
        tool_allowlist=allowed,
        max_steps=6,
        parallel_tool_calls=True,
        system_prompt=None,
    )

    task = "What's trending today in the stock market? Use tools as needed, and give 3 bullet points with links."
    result = agent.process_task(task)

    print("\n=== Final ===")
    print(result["final"])


if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY not set. Add it to .env or export it.")
    main()