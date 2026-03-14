"""Tests for feed discovery module."""

from unittest.mock import patch

import pytest

from rss_reader.discovery import (
    DiscoveredFeed,
    _detect_feed_type,
    _sort_feeds,
    discover_feeds,
    parse_link_tags,
    parse_sitemap_for_feeds,
    resolve_feed_url,
)
from rss_reader.feed import FeedError


# --- HTML fixtures ---

HTML_WITH_ATOM_LINK = """
<html>
<head>
    <link rel="alternate" type="application/atom+xml" title="My Atom Feed" href="/feed.xml">
</head>
<body></body>
</html>
"""

HTML_WITH_RSS_LINK = """
<html>
<head>
    <link rel="alternate" type="application/rss+xml" title="My RSS Feed" href="/rss.xml">
</head>
<body></body>
</html>
"""

HTML_WITH_MULTIPLE_LINKS = """
<html>
<head>
    <link rel="alternate" type="application/atom+xml" title="Atom Feed" href="/atom.xml">
    <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="/rss.xml">
    <link rel="alternate" type="application/rss+xml" title="Comments RSS" href="/comments/feed">
</head>
<body></body>
</html>
"""

HTML_WITH_NO_FEED_LINKS = """
<html>
<head>
    <link rel="stylesheet" href="/style.css">
    <link rel="icon" href="/favicon.ico">
</head>
<body></body>
</html>
"""

HTML_WITH_RELATIVE_URL = """
<html>
<head>
    <link rel="alternate" type="application/atom+xml" title="Feed" href="feed.xml">
</head>
<body></body>
</html>
"""

HTML_WITH_NO_HREF = """
<html>
<head>
    <link rel="alternate" type="application/rss+xml" title="Bad Link">
</head>
<body></body>
</html>
"""


RSS_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <item>
      <title>Post 1</title>
      <link>https://example.com/1</link>
      <guid>1</guid>
      <description>Content</description>
    </item>
  </channel>
</rss>"""

ATOM_CONTENT = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Atom Feed</title>
  <link href="https://example.com"/>
  <entry>
    <title>Entry 1</title>
    <link href="https://example.com/1"/>
    <id>1</id>
    <summary>Content</summary>
  </entry>
</feed>"""


SITEMAP_WITH_FEEDS = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/feed.xml</loc></url>
  <url><loc>https://example.com/blog/rss</loc></url>
</urlset>
"""

SITEMAP_NO_FEEDS = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/</loc></url>
  <url><loc>https://example.com/about</loc></url>
  <url><loc>https://example.com/contact</loc></url>
</urlset>
"""


# --- Test parse_link_tags ---


class TestParseLinkTags:
    def test_atom_link(self):
        feeds = parse_link_tags(HTML_WITH_ATOM_LINK, "https://example.com")
        assert len(feeds) == 1
        assert feeds[0].url == "https://example.com/feed.xml"
        assert feeds[0].title == "My Atom Feed"
        assert feeds[0].feed_type == "atom"

    def test_rss_link(self):
        feeds = parse_link_tags(HTML_WITH_RSS_LINK, "https://example.com")
        assert len(feeds) == 1
        assert feeds[0].url == "https://example.com/rss.xml"
        assert feeds[0].feed_type == "rss"

    def test_multiple_links(self):
        feeds = parse_link_tags(HTML_WITH_MULTIPLE_LINKS, "https://example.com")
        assert len(feeds) == 3
        types = [f.feed_type for f in feeds]
        assert "atom" in types
        assert "rss" in types

    def test_no_feed_links(self):
        feeds = parse_link_tags(HTML_WITH_NO_FEED_LINKS, "https://example.com")
        assert len(feeds) == 0

    def test_relative_url_resolved(self):
        feeds = parse_link_tags(HTML_WITH_RELATIVE_URL, "https://example.com/blog/")
        assert len(feeds) == 1
        assert feeds[0].url == "https://example.com/blog/feed.xml"

    def test_no_href_skipped(self):
        feeds = parse_link_tags(HTML_WITH_NO_HREF, "https://example.com")
        assert len(feeds) == 0


# --- Test well-known path probing ---


class TestWellKnownPaths:
    def test_valid_feed_found(self):
        """When a well-known path returns a valid feed, it should be discovered."""
        feed_info = {"title": "Found Feed", "link": "https://example.com"}

        def mock_validate(url):
            return url.endswith("/feed.xml")

        with (
            patch(
                "rss_reader.discovery._validate_feed_url",
                side_effect=mock_validate,
            ),
            patch(
                "rss_reader.discovery.fetch_and_parse",
                return_value=(feed_info, []),
            ),
            patch(
                "rss_reader.discovery.fetch_feed_content",
                return_value=RSS_CONTENT,
            ),
        ):
            from rss_reader.discovery import _discover_from_well_known_paths

            feeds = _discover_from_well_known_paths("https://example.com")
            # Only /feed.xml matches
            assert len(feeds) == 1
            assert feeds[0].title == "Found Feed"

    def test_no_valid_paths(self):
        """When no well-known paths return valid feeds, returns empty."""
        with patch("rss_reader.discovery._validate_feed_url", return_value=False):
            from rss_reader.discovery import _discover_from_well_known_paths

            feeds = _discover_from_well_known_paths("https://example.com")
            assert len(feeds) == 0


# --- Test sitemap discovery ---


class TestSitemapDiscovery:
    def test_feeds_found_in_sitemap(self):
        feed_info = {"title": "Sitemap Feed", "link": "https://example.com"}

        with (
            patch(
                "rss_reader.discovery.fetch_and_parse",
                return_value=(feed_info, []),
            ),
            patch(
                "rss_reader.discovery.fetch_feed_content",
                return_value=RSS_CONTENT,
            ),
        ):
            feeds = parse_sitemap_for_feeds(SITEMAP_WITH_FEEDS, "https://example.com")
            assert len(feeds) == 2  # feed.xml and blog/rss
            urls = [f.url for f in feeds]
            assert "https://example.com/feed.xml" in urls
            assert "https://example.com/blog/rss" in urls

    def test_no_feeds_in_sitemap(self):
        feeds = parse_sitemap_for_feeds(SITEMAP_NO_FEEDS, "https://example.com")
        assert len(feeds) == 0

    def test_invalid_feed_url_in_sitemap_skipped(self):
        with patch(
            "rss_reader.discovery.fetch_and_parse",
            side_effect=FeedError("Invalid feed"),
        ):
            feeds = parse_sitemap_for_feeds(SITEMAP_WITH_FEEDS, "https://example.com")
            assert len(feeds) == 0


# --- Test discovery chain ---


class TestDiscoverFeeds:
    def test_link_tags_stop_early(self):
        """If link tags find feeds, well-known paths and sitemap are not tried."""
        link_feeds = [
            DiscoveredFeed(url="https://example.com/feed", title="Feed", feed_type="atom")
        ]
        with (
            patch("rss_reader.discovery._discover_from_link_tags", return_value=link_feeds),
            patch("rss_reader.discovery._discover_from_well_known_paths") as mock_wk,
            patch("rss_reader.discovery._discover_from_sitemap") as mock_sm,
        ):
            feeds = discover_feeds("https://example.com")
            assert len(feeds) == 1
            mock_wk.assert_not_called()
            mock_sm.assert_not_called()

    def test_falls_through_to_well_known(self):
        """If link tags find nothing, well-known paths are tried."""
        wk_feeds = [
            DiscoveredFeed(url="https://example.com/feed.xml", title="Feed", feed_type="rss")
        ]
        with (
            patch("rss_reader.discovery._discover_from_link_tags", return_value=[]),
            patch("rss_reader.discovery._discover_from_well_known_paths", return_value=wk_feeds),
            patch("rss_reader.discovery._discover_from_sitemap") as mock_sm,
        ):
            feeds = discover_feeds("https://example.com")
            assert len(feeds) == 1
            mock_sm.assert_not_called()

    def test_falls_through_to_sitemap(self):
        """If link tags and well-known paths find nothing, sitemap is tried."""
        sm_feeds = [
            DiscoveredFeed(url="https://example.com/feed", title="Feed", feed_type="rss")
        ]
        with (
            patch("rss_reader.discovery._discover_from_link_tags", return_value=[]),
            patch("rss_reader.discovery._discover_from_well_known_paths", return_value=[]),
            patch("rss_reader.discovery._discover_from_sitemap", return_value=sm_feeds),
        ):
            feeds = discover_feeds("https://example.com")
            assert len(feeds) == 1

    def test_nothing_found(self):
        with (
            patch("rss_reader.discovery._discover_from_link_tags", return_value=[]),
            patch("rss_reader.discovery._discover_from_well_known_paths", return_value=[]),
            patch("rss_reader.discovery._discover_from_sitemap", return_value=[]),
        ):
            feeds = discover_feeds("https://example.com")
            assert len(feeds) == 0


class TestResolveFeedUrl:
    def test_direct_feed_url(self):
        """If URL is a valid feed, returns tuple directly."""
        feed_info = {"title": "Direct Feed", "link": "https://example.com"}
        with patch(
            "rss_reader.discovery.fetch_and_parse",
            return_value=(feed_info, [{"guid": "1", "title": "P"}]),
        ):
            result = resolve_feed_url("https://example.com/feed.xml")
            assert isinstance(result, tuple)
            assert result[0] == "https://example.com/feed.xml"
            assert result[1]["title"] == "Direct Feed"

    def test_website_url_triggers_discovery(self):
        """If URL is not a feed, runs discovery."""
        discovered = [
            DiscoveredFeed(url="https://example.com/feed.xml", title="Found", feed_type="atom")
        ]
        with (
            patch("rss_reader.discovery.fetch_and_parse", side_effect=FeedError("Not a feed")),
            patch("rss_reader.discovery.discover_feeds", return_value=discovered),
        ):
            result = resolve_feed_url("https://example.com")
            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].title == "Found"


# --- Test feed sorting ---


class TestFeedSorting:
    def test_atom_before_rss(self):
        feeds = [
            DiscoveredFeed(url="https://a.com/rss", title="RSS Feed", feed_type="rss"),
            DiscoveredFeed(url="https://a.com/atom", title="Atom Feed", feed_type="atom"),
        ]
        sorted_feeds = _sort_feeds(feeds)
        assert sorted_feeds[0].feed_type == "atom"
        assert sorted_feeds[1].feed_type == "rss"

    def test_same_type_sorted_by_title(self):
        feeds = [
            DiscoveredFeed(url="https://a.com/b", title="Beta", feed_type="rss"),
            DiscoveredFeed(url="https://a.com/a", title="Alpha", feed_type="rss"),
        ]
        sorted_feeds = _sort_feeds(feeds)
        assert sorted_feeds[0].title == "Alpha"
        assert sorted_feeds[1].title == "Beta"


# --- Test feed type detection ---


class TestDetectFeedType:
    def test_detect_atom(self):
        assert _detect_feed_type(ATOM_CONTENT) == "atom"

    def test_detect_rss(self):
        assert _detect_feed_type(RSS_CONTENT) == "rss"

    def test_unknown_defaults_to_rss(self):
        assert _detect_feed_type("some random content") == "rss"
