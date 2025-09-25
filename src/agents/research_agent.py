from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, LLMProvider, MemoryStore
from ..tools.base_tool import BaseTool
from ..tools.registry import registry


class ResearchAgent(BaseAgent):
    
    """
    A simple research agent that:
      1) Searches the web for the task/topic
      2) Scrapes the first result
      3) Asks the LLM to summarize
    """

    def __init__(
        self,
        name: str,
        config: Dict[str, Any],
        llm: Optional[LLMProvider] = None,
        tools: Optional[List[BaseTool]] = None,
        memory: Optional[MemoryStore] = None,
        **kwargs  # Accept additional parameters that AgentFactory might pass
    ) -> None:
        super().__init__(name=name, config=config, llm=llm, tools=tools, memory=memory)

        # If tools are not provided, pick defaults from the global registry
        if not self.tools:
            wanted = ["web.search", "web.scrape"]
            self.tools = [registry.get_tool(n) for n in wanted if registry.has_tool(n)]

        # Build a quick lookup by name
        self._tool_by_name: Dict[str, BaseTool] = {t.name: t for t in self.tools}

    def process_task(self, task: str) -> Any:
        """
        Synchronous entrypoint for compatibility with the provided BaseAgent signature.

        This method uses asyncio.run to execute async tool calls. If you integrate this
        in an async server (e.g., FastAPI), consider converting this to async end-to-end.
        """
        return self._run_sync(self._process_task_async(task))

    async def _process_task_async(self, task: str) -> Dict[str, Any]:
        # 1) Search the web
        search_tool = self._require_tool("web.search")
        search_payload = {
            "query": task,
            "max_results": int(self.config.get("max_results", 5)),
            "safe": True,
        }
        
        search_out = await search_tool(search_payload)

        if not search_out.items:
            summary = f"No results found for query: {search_out.query!r}"
            if self.llm:
                summary = self.llm.send_message(summary)
            self.update_memory("last_research", {"query": task, "results": [], "summary": summary})
            return {
                "agent": self.name,
                "query": search_out.query,
                "results": [],
                "summary": summary,
            }

        top = search_out.items[0]
        # 2) Scrape the top result
        scraper_tool = self._require_tool("web.scrape")
        scrape_payload = {"url": top.url, "css_selectors": ["article", "main"], "max_chars": 8000}
        scrape_out = await scraper_tool(scrape_payload)

        # 3) Summarize with LLM (or fallback if no LLM provided)
        prompt = self._build_summary_prompt(task, search_out, scrape_out)
        if self.llm:
            summary = self.llm.send_message(prompt)
        else:
            summary = f"[No LLM configured]\n{prompt}"

        # Update memory
        self.update_memory(
            "last_research",
            {
                "query": task,
                "top_result": {"title": top.title, "url": top.url},
                "summary": summary,
            },
        )

        return {
            "agent": self.name,
            "query": task,
            "top_result": {"title": top.title, "url": top.url},
            "summary": summary,
        }

    def handle_tool_calls(self, tool_name: str, payload: Dict[str, Any]) -> Any:
        """
        Execute a named tool with the given payload and return the result.

        This is a sync wrapper around the tool's async call for compatibility.
        """
        tool = self._require_tool(tool_name)
        return self._run_sync(tool(payload))

    # Helpers ------------------------------------------------------------------

    def _require_tool(self, name: str) -> BaseTool:
        tool = self._tool_by_name.get(name)
        if tool is None:
            # Try the global registry as fallback
            if registry.has_tool(name):
                tool = registry.get_tool(name)
                self._tool_by_name[name] = tool
            else:
                raise ValueError(f"Tool '{name}' not available to agent '{self.name}'.")
        return tool

    def _build_summary_prompt(self, task: str, search_out: Any, scrape_out: Any) -> str:
        lines: List[str] = []
        lines.append(f"Task: {task}")
        lines.append("")
        lines.append("Top search results:")
        for item in search_out.items[:5]:
            lines.append(f"- ({item.position}) {item.title} — {item.url}")
        lines.append("")
        lines.append(f"Scraped page title: {scrape_out.title or 'N/A'}")
        lines.append("Scraped content (truncated):")
        content = scrape_out.content[:2000]
        lines.append(content)
        lines.append("")
        lines.append("Please provide a concise summary of the content above,")
        lines.append("including 3-5 key bullet points and any notable sources.")
        return "\n".join(lines)

    def _run_sync(self, coro):
        """
        Run an async coroutine in sync context.
        - If no event loop is running, uses asyncio.run
        - If already inside an event loop, create a task and wait
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        # If we're already in an event loop, run it safely
        return loop.run_until_complete(coro)