from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from ..base_tool import BaseTool
from ..registry import registry


class FeedItem(BaseModel):
    title: str = Field(..., description="Item title")
    link: str = Field(..., description="Item link (absolute URL)")
    published: Optional[str] = Field(None, description="Published date/time string if available")


class RSSInput(BaseModel):
    url: str = Field(..., description="RSS/Atom feed URL")
    max_items: int = Field(10, ge=1, le=50, description="Maximum items to return")
    timeout_ms: int = Field(8000, ge=1000, le=60000, description="HTTP timeout in ms")
    user_agent: Optional[str] = Field(None, description="Optional User-Agent header")


class RSSOutput(BaseModel):
    title: Optional[str] = Field(None, description="Feed title if available")
    items: List[FeedItem] = Field(default_factory=list, description="Feed items (up to max_items)")


class RSSTool(BaseTool[RSSInput, RSSOutput]):
    name = "web.rss"
    description = "Fetch and parse an RSS/Atom feed and return recent items."
    input_model = RSSInput
    output_model = RSSOutput

    requires_network = True
    requires_filesystem = False
    timeout_seconds = 15.0
    max_concurrency = 8
    tags = frozenset({"web", "rss", "news"})

    async def execute(self, params: RSSInput, *, context: Optional[dict] = None) -> RSSOutput:
        headers = {
            "User-Agent": params.user_agent
            or "Mozilla/5.0 (compatible; FlexyGentRSS/0.1; +https://example.com/bot)",
            "Accept": "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8",
        }
        timeout = httpx.Timeout(params.timeout_ms / 1000.0)
        async with httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(params.url)
            xml = resp.text

        soup = BeautifulSoup(xml, "xml")

        # Try Atom then RSS styles
        feed_title = None
        title_el = soup.find("title")
        if title_el and title_el.text:
            feed_title = title_el.text.strip()

        items_out: List[FeedItem] = []
        entries = soup.find_all(["entry", "item"])
        for e in entries:
            # Title
            t_el = e.find("title")
            title = t_el.text.strip() if t_el and t_el.text else "Untitled"

            # Link
            link = None
            link_el = e.find("link")
            if link_el:
                # Atom link rel="alternate" href
                href = link_el.get("href") or link_el.text
                if href:
                    link = href.strip()
            if not link:
                guid = e.find("guid")
                if guid and guid.text:
                    link = guid.text.strip()
            if not link:
                # Fallback try any <link> text
                ltext = e.find("link")
                if ltext and ltext.text:
                    link = ltext.text.strip()
            if not link:
                continue
            link = urljoin(params.url, link)

            # Published
            pub = None
            for tag in ("updated", "published", "pubDate", "dc:date"):
                el = e.find(tag)
                if el and el.text:
                    pub = el.text.strip()
                    break
            items_out.append(FeedItem(title=title, link=link, published=pub))
            if len(items_out) >= params.max_items:
                break

        return RSSOutput(title=feed_title, items=items_out)


# Auto-register
registry.register_tool(RSSTool())