from __future__ import annotations

import re
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


class ScrapeInput(BaseModel):
    url: str = Field(..., description="Target URL to fetch and extract text from")
    css_selectors: Optional[List[str]] = Field(
        None,
        description="Optional CSS selectors to focus extraction (e.g., ['article', '#content']). If omitted, uses a heuristic.",
    )
    include_links: bool = Field(True, description="Whether to include discovered hyperlinks in output")
    max_chars: int = Field(16_000, ge=1000, le=200_000, description="Trim extracted text to this many characters")
    timeout_ms: int = Field(10000, ge=1000, le=60000, description="HTTP timeout for the fetch in ms")
    user_agent: Optional[str] = Field(
        None,
        description="Optional custom User-Agent header",
    )
    strip_whitespace: bool = Field(True, description="Collapse whitespace in extracted text")


class LinkItem(BaseModel):
    href: str = Field(..., description="Absolute URL of the link")
    text: Optional[str] = Field(None, description="Visible link text")


class ScrapeOutput(BaseModel):
    title: Optional[str] = Field(None, description="Page title if available")
    content: str = Field(..., description="Extracted text content")
    links: Optional[List[LinkItem]] = Field(default=None, description="List of links if include_links=True")
    content_type: Optional[str] = Field(None, description="HTTP Content-Type header")
    status_code: int = Field(..., description="HTTP status code")


class ScraperTool(BaseTool[ScrapeInput, ScrapeOutput]):
    name = "web.scrape"
    description = "Fetch a web page and extract readable text and links."
    input_model = ScrapeInput
    output_model = ScrapeOutput

    requires_network = True
    requires_filesystem = False
    timeout_seconds = 20.0
    max_concurrency = 8
    tags = frozenset({"web", "scraper", "html"})

    async def execute(self, params: ScrapeInput, *, context: Optional[dict] = None) -> ScrapeOutput:
        headers = {
            "User-Agent": params.user_agent
            or "Mozilla/5.0 (compatible; MultiAgentScraper/0.1; +https://example.com/bot)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        timeout = httpx.Timeout(params.timeout_ms / 1000.0)

        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(params.url)
            status_code = resp.status_code
            content_type = resp.headers.get("Content-Type", "")

            # Only attempt HTML parsing for HTML-like content types
            is_html = "text/html" in content_type or "application/xhtml+xml" in content_type
            if not is_html:
                # Return text body truncated, no HTML parsing
                text = resp.text
                if params.strip_whitespace:
                    text = _collapse_whitespace(text)
                if len(text) > params.max_chars:
                    text = text[: params.max_chars]
                return ScrapeOutput(
                    title=None,
                    content=text,
                    links=None,
                    content_type=content_type,
                    status_code=status_code,
                )

            html = resp.text

        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts/styles
        for tag in soup(["script", "style", "noscript", "template"]):
            tag.extract()

        # Title
        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Select content
        nodes: List = []
        if params.css_selectors:
            for sel in params.css_selectors:
                nodes.extend(soup.select(sel))
        else:
            # Heuristic: prefer <article>, then <main>, else the largest text block
            article = soup.select_one("article")
            if article:
                nodes = [article]
            else:
                main = soup.select_one("main")
                if main:
                    nodes = [main]
                else:
                    # Fall back to body
                    nodes = [soup.body or soup]

        # Extract text
        texts: List[str] = []
        for node in nodes:
            # Get paragraph-level text
            ps = node.find_all(["p", "li", "h1", "h2", "h3", "h4", "h5"])
            if ps:
                for p in ps:
                    txt = p.get_text(" ", strip=True)
                    if txt:
                        texts.append(txt)
            else:
                txt = node.get_text(" ", strip=True)
                if txt:
                    texts.append(txt)

        content = "\n".join(texts) if texts else (soup.get_text(" ", strip=True) or "")

        if params.strip_whitespace:
            # Normalize excessive whitespace/newlines
            content = re.sub(r"[ \t]+", " ", content)
            content = re.sub(r"\n{3,}", "\n\n", content).strip()

        if len(content) > params.max_chars:
            content = content[: params.max_chars]

        links_out: Optional[List[LinkItem]] = None
        if params.include_links:
            links_out = []
            for a in soup.find_all("a", href=True):
                href = urljoin(params.url, a["href"])
                text = a.get_text(" ", strip=True) or None
                links_out.append(LinkItem(href=href, text=text))

        return ScrapeOutput(
            title=title,
            content=content,
            links=links_out,
            content_type=content_type,
            status_code=200,
        )


# Auto-register at import time
# registry.register_tool(ScraperTool())