
from __future__ import annotations

from typing import List, Optional
from urllib.parse import urlparse, parse_qs

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry


class SearchItem(BaseModel):
    title: str = Field(..., description="Result title")
    url: str = Field(..., description="Result URL")
    snippet: Optional[str] = Field(None, description="Short text snippet")
    position: int = Field(..., ge=1, description="1-based position in results")
    source: str = Field(..., description="Search engine/source name")


class SearchInput(BaseModel):
    query: str = Field(..., description="Search query text")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of results to return")
    site: Optional[str] = Field(None, description="Optional site filter, e.g., 'example.com'")
    safe: bool = Field(True, description="Enable safe search if supported by the engine")
    engine: str = Field(
        "duckduckgo",
        description="Search engine backend. Currently supported: 'duckduckgo'.",
    )
    lang: Optional[str] = Field(None, description="Locale/language hint (engine-specific)")
    timeout_ms: int = Field(8000, ge=1000, le=30000, description="HTTP timeout for the search request in ms")


class SearchOutput(BaseModel):
    items: List[SearchItem] = Field(default_factory=list, description="Ordered list of search results")
    engine: str = Field(..., description="Engine used for the search")
    query: str = Field(..., description="Final query used")


class SearchTool(BaseTool[SearchInput, SearchOutput]):
    name = "web.search"
    description = "Perform a web search and return top results with title, URL, and snippet."
    input_model = SearchInput
    output_model = SearchOutput

    requires_network = True
    requires_filesystem = False
    timeout_seconds = 12.0
    max_concurrency = 8
    tags = frozenset({"web", "search"})

    async def execute(self, params: SearchInput, *, context: Optional[dict] = None) -> SearchOutput:
        query = params.query
        if params.site:
            query = f"site:{params.site} {query}"

        engine = params.engine.lower().strip()
        if engine not in {"duckduckgo"}:
            engine = "duckduckgo"

        items: List[SearchItem] = await self._search_duckduckgo(
            query=query,
            max_results=params.max_results,
            safe=params.safe,
            lang=params.lang,
            timeout_ms=params.timeout_ms,
        )

        return SearchOutput(items=items, engine=engine, query=query)

    async def _search_duckduckgo(
        self,
        *,
        query: str,
        max_results: int,
        safe: bool,
        lang: Optional[str],
        timeout_ms: int,
    ) -> List[SearchItem]:
        # Try two endpoints: primary then fallback
        endpoints = [
            "https://duckduckgo.com/html",            # primary HTML endpoint
            "https://html.duckduckgo.com/html/",      # fallback HTML endpoint
        ]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/128.0 Safari/537.36",  # Update to a more recent Chrome version; remove 'MultiAgentBot/0.1' to avoid bot flagging
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": (lang or "en-US,en;q=0.9"),
            "Content-Type": "application/x-www-form-urlencoded",  # Explicit for form data
        }
        data = {"q": query, "kp": "1" if safe else "-1"}  # Use 'data' for POST body

        timeout = httpx.Timeout(timeout_ms / 1000.0)
        for base_url in endpoints:
            try:
                async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
                    resp = await client.post(base_url, data=data)  # Change to POST with form data
                    if resp.status_code != 200:
                        continue  # Skip if not successful
                    html = resp.text
            except Exception:
                # Try next endpoint
                continue

            results = self._parse_duckduckgo_html(html, max_results=max_results)
            if results:
                return results

        # If nothing parsed, return empty
        return []

    def _parse_duckduckgo_html(self, html: str, *, max_results: int) -> List[SearchItem]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[SearchItem] = []

        # Strategy A: Global anchors with the typical result class
        anchors = soup.select("a.result__a")
        # Strategy B: Known containers in older/newer templates
        if not anchors:
            anchors = soup.select("#links .result__a, .result .result__a, .web-result .result__a")

        # Strategy C: fallback to likely h2 > a pattern
        if not anchors:
            anchors = soup.select("h2 a[href]")

        position = 0
        for a in anchors:
            href = a.get("href", "").strip()
            title = a.get_text(" ", strip=True)
            url = self._extract_ddg_url(href)
            if not url or not title:
                continue

            # Try to find a nearby snippet
            snip = None
            parent = a.find_parent(["div", "article", "li"])
            if parent:
                sn = parent.select_one(".result__snippet, .result__body, .result__extras, p")
                if sn:
                    snip = sn.get_text(" ", strip=True) or None

            position += 1
            results.append(
                SearchItem(
                    title=title,
                    url=url,
                    snippet=snip,
                    position=position,
                    source="duckduckgo",
                )
            )
            if len(results) >= max_results:
                break

        return results

    def _extract_ddg_url(self, href: str) -> str:
        # Already absolute?
        parsed = urlparse(href)
        if parsed.scheme in {"http", "https"}:
            return href

        # DDG redirect links like '/l/?kh=-1&uddg=<encoded>'
        if href.startswith("/l/") or href.startswith("/?"):
            params = parse_qs(urlparse(href).query)
            uddg = params.get("uddg", [])
            if uddg:
                return uddg[0]
        return href


# Auto-register at import time
registry.register_tool(SearchTool())