"""Feed discovery module.

Discovers RSS/Atom feed URLs from a plain website URL using:
1. HTML <link rel="alternate"> tags
2. Well-known feed URL paths
3. Sitemap inspection
"""

import warnings
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from rss_reader.feed import FeedError, fetch_and_parse, fetch_feed_content


@dataclass
class DiscoveredFeed:
    """A feed discovered from a website."""

    url: str
    title: str
    feed_type: str  # "atom" or "rss"


WELL_KNOWN_PATHS = [
    "/feed",
    "/rss",
    "/atom.xml",
    "/feed.xml",
    "/rss.xml",
    "/index.xml",
    "/feed/atom",
    "/feed/rss",
]

FEED_LINK_TYPES = {
    "application/atom+xml": "atom",
    "application/rss+xml": "rss",
}


def discover_feeds(url: str) -> list[DiscoveredFeed]:
    """Discover RSS/Atom feeds from a website URL.

    Tries strategies in order: HTML link tags, well-known paths, sitemap.
    Returns discovered feeds sorted with Atom preferred over RSS.
    """
    feeds: list[DiscoveredFeed] = []

    # Strategy 1: HTML link tags
    feeds = _discover_from_link_tags(url)
    if feeds:
        return _sort_feeds(feeds)

    # Strategy 2: Well-known paths
    feeds = _discover_from_well_known_paths(url)
    if feeds:
        return _sort_feeds(feeds)

    # Strategy 3: Sitemap
    feeds = _discover_from_sitemap(url)
    return _sort_feeds(feeds)


def resolve_feed_url(url: str) -> tuple[str, dict, list[dict]] | list[DiscoveredFeed]:
    """Try to use URL as a direct feed first; if that fails, run discovery.

    Returns either:
    - A tuple of (url, feed_info, entries) if URL is a direct feed
    - A list of DiscoveredFeed if discovery found feeds
    - An empty list if nothing was found
    """
    # First, try as a direct feed
    try:
        feed_info, entries = fetch_and_parse(url)
        return (url, feed_info, entries)
    except FeedError:
        pass

    # Not a feed, run discovery
    return discover_feeds(url)


def _fetch_page(url: str, timeout: float = 10.0) -> str | None:
    """Fetch a page, returning None on any error."""
    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()
        return response.text
    except (httpx.HTTPError, httpx.TimeoutException):
        return None


def _discover_from_link_tags(url: str) -> list[DiscoveredFeed]:
    """Discover feeds from HTML <link rel="alternate"> tags."""
    html = _fetch_page(url)
    if not html:
        return []

    return parse_link_tags(html, url)


def parse_link_tags(html: str, base_url: str) -> list[DiscoveredFeed]:
    """Parse HTML and extract feed URLs from link tags."""
    soup = BeautifulSoup(html, "html.parser")
    feeds: list[DiscoveredFeed] = []

    for link in soup.find_all("link", rel="alternate"):
        link_type = (link.get("type") or "").lower()
        href = link.get("href")
        if not href or link_type not in FEED_LINK_TYPES:
            continue

        feed_url = urljoin(base_url, href)
        title = link.get("title") or feed_url
        feed_type = FEED_LINK_TYPES[link_type]
        feeds.append(DiscoveredFeed(url=feed_url, title=title, feed_type=feed_type))

    return feeds


def _discover_from_well_known_paths(url: str) -> list[DiscoveredFeed]:
    """Probe well-known feed paths and validate them."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    feeds: list[DiscoveredFeed] = []

    for path in WELL_KNOWN_PATHS:
        candidate_url = urljoin(base, path)
        if _validate_feed_url(candidate_url):
            feeds.append(
                DiscoveredFeed(
                    url=candidate_url,
                    title=candidate_url,
                    feed_type="unknown",
                )
            )

    # Resolve actual feed types and titles
    resolved: list[DiscoveredFeed] = []
    for feed in feeds:
        try:
            feed_info, _ = fetch_and_parse(feed.url)
            title = feed_info.get("title", feed.url)
            # Determine type by trying to detect from content
            content = fetch_feed_content(feed.url)
            feed_type = _detect_feed_type(content)
            resolved.append(
                DiscoveredFeed(url=feed.url, title=title, feed_type=feed_type)
            )
        except FeedError:
            continue

    return resolved


def _validate_feed_url(url: str) -> bool:
    """Check if a URL returns feed-like content using a HEAD then GET."""
    try:
        response = httpx.head(url, timeout=10.0, follow_redirects=True)
        if response.status_code >= 400:
            return False
    except (httpx.HTTPError, httpx.TimeoutException):
        return False

    # Validate by actually parsing
    try:
        fetch_and_parse(url)
        return True
    except FeedError:
        return False


def _discover_from_sitemap(url: str) -> list[DiscoveredFeed]:
    """Discover feeds by inspecting the site's sitemap.xml."""
    parsed = urlparse(url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"
    xml = _fetch_page(sitemap_url)
    if not xml:
        return []

    return parse_sitemap_for_feeds(xml, url)


def parse_sitemap_for_feeds(xml: str, base_url: str) -> list[DiscoveredFeed]:
    """Parse sitemap XML and look for feed-like URLs."""
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(xml, "html.parser")
    feed_patterns = ["/feed", "/rss", "/atom"]
    feeds: list[DiscoveredFeed] = []
    seen_urls: set[str] = set()

    for loc in soup.find_all("loc"):
        loc_url = loc.get_text(strip=True)
        if not loc_url:
            continue

        # Check if URL path looks feed-like
        path = urlparse(loc_url).path.lower()
        if any(pattern in path for pattern in feed_patterns):
            if loc_url in seen_urls:
                continue
            seen_urls.add(loc_url)

            # Validate it's actually a feed
            try:
                feed_info, _ = fetch_and_parse(loc_url)
                content = fetch_feed_content(loc_url)
                feed_type = _detect_feed_type(content)
                feeds.append(
                    DiscoveredFeed(
                        url=loc_url,
                        title=feed_info.get("title", loc_url),
                        feed_type=feed_type,
                    )
                )
            except FeedError:
                continue

    return feeds


def _detect_feed_type(content: str) -> str:
    """Detect whether feed content is Atom or RSS."""
    # Simple heuristic: Atom feeds have <feed> root, RSS has <rss>
    content_lower = content[:500].lower()
    if "<feed" in content_lower:
        return "atom"
    if "<rss" in content_lower:
        return "rss"
    return "rss"  # default


def _sort_feeds(feeds: list[DiscoveredFeed]) -> list[DiscoveredFeed]:
    """Sort feeds with Atom preferred over RSS."""
    return sorted(feeds, key=lambda f: (0 if f.feed_type == "atom" else 1, f.title))
