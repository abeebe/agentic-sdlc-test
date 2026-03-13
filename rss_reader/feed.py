from datetime import datetime
from time import mktime
from typing import Optional

import feedparser
import httpx

from rss_reader.models import Article


class FeedError(Exception):
    pass


def fetch_feed_content(url: str, timeout: float = 15.0) -> str:
    """Fetch raw feed content from a URL."""
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except httpx.TimeoutException:
        raise FeedError(f"Timeout fetching {url}")
    except httpx.HTTPStatusError as e:
        raise FeedError(f"HTTP {e.response.status_code} fetching {url}")
    except httpx.RequestError as e:
        raise FeedError(f"Network error fetching {url}: {e}")


def parse_feed(content: str, url: str = "") -> tuple[dict, list[dict]]:
    """Parse feed content and return (feed_info, entries).

    feed_info: dict with title, link
    entries: list of dicts with guid, title, link, author, published, summary
    """
    parsed = feedparser.parse(content)

    if not parsed.entries and (
        parsed.bozo or not parsed.feed.get("title")
    ):
        raise FeedError(f"Malformed feed content from {url}")

    feed_info = {
        "title": parsed.feed.get("title", url),
        "link": parsed.feed.get("link", ""),
    }

    entries = []
    for entry in parsed.entries:
        published = _parse_date(entry)
        summary = entry.get("summary", "") or entry.get("content", [{}])[0].get(
            "value", ""
        ) if entry.get("content") else entry.get("summary", "")

        entries.append(
            {
                "guid": entry.get("id", entry.get("link", "")),
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "author": entry.get("author"),
                "published": published,
                "summary": summary or "",
            }
        )

    return feed_info, entries


def _parse_date(entry: dict) -> Optional[datetime]:
    """Extract and parse publication date from a feed entry."""
    for field in ("published_parsed", "updated_parsed"):
        time_struct = entry.get(field)
        if time_struct:
            try:
                return datetime.fromtimestamp(mktime(time_struct))
            except (ValueError, OverflowError):
                continue
    return None


def fetch_and_parse(url: str) -> tuple[dict, list[dict]]:
    """Fetch and parse a feed URL. Returns (feed_info, entries)."""
    content = fetch_feed_content(url)
    return parse_feed(content, url)


def entries_to_articles(entries: list[dict], feed_id: int) -> list[Article]:
    """Convert parsed entries to Article objects."""
    return [
        Article(
            id=None,
            feed_id=feed_id,
            guid=e["guid"],
            title=e["title"],
            link=e["link"],
            author=e["author"],
            published=e["published"],
            summary=e["summary"],
        )
        for e in entries
    ]
