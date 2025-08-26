from __future__ import annotations

import asyncio

from src.tools import load_builtin_tools, registry
from src.llm.provider import SimpleLLMProvider
from src.agents.research_agent import ResearchAgent


def main():
    # Load tools (web.search, web.scrape, etc.)
    load_builtin_tools()

    # Initialize a simple LLM
    llm = SimpleLLMProvider(max_output_chars=600)

    # Create agent with default config
    agent = ResearchAgent(
        name="researcher",
        config={"max_results": 5},
        llm=llm,
        tools=[registry.get_tool("web.search"), registry.get_tool("web.scrape")],
        memory=None,  # You can plug in a real memory store later
    )

    # Run a task
    task = "Latest developments in agentic AI frameworks 2025"
    result = agent.process_task(task)

    print("=== Agent Result ===")
    print(result["summary"])


if __name__ == "__main__":
    main()