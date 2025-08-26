from __future__ import annotations
import os

# Load .env in dev; no-op if missing
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from src.tools.web import search as _search  # noqa: F401
from src.tools.web import scraper as _scraper  # noqa: F401
from src.tools.registry import registry
from src.llm.openrouter_provider import OpenRouterProvider
from src.agents.research_agent import ResearchAgent
from src.utils.config_loader import load_config, get_openrouter_cfg

def main():
    cfg = load_config(["config/default.yaml"])
    or_cfg = get_openrouter_cfg(cfg)
    llm = OpenRouterProvider.from_config(or_cfg)

    agent = ResearchAgent(
        name="researcher",
        config={"max_results": 5},
        llm=llm,
        tools=[registry.get_tool("web.search"), registry.get_tool("web.scrape")],
        memory=None,
    )

    result = agent.process_task("Latest developments in agentic AI frameworks 2025")
    print("\n=== Agent Result ===")
    print(result["summary"])

if __name__ == "__main__":
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: OPENROUTER_API_KEY not set. Add it to .env or export it.")
    main()