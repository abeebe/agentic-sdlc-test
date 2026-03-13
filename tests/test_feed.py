import pytest

from rss_reader.feed import FeedError, entries_to_articles, parse_feed

RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test RSS Feed</title>
    <link>https://example.com</link>
    <description>A test feed</description>
    <item>
      <title>First Post</title>
      <link>https://example.com/post-1</link>
      <guid>post-1</guid>
      <pubDate>Mon, 15 Jan 2025 12:00:00 GMT</pubDate>
      <description>This is the first post.</description>
    </item>
    <item>
      <title>Second Post</title>
      <link>https://example.com/post-2</link>
      <guid>post-2</guid>
      <pubDate>Tue, 16 Jan 2025 12:00:00 GMT</pubDate>
      <description>This is the second post.</description>
    </item>
  </channel>
</rss>"""

ATOM_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Atom Feed</title>
  <link href="https://example.com"/>
  <entry>
    <title>Atom Entry</title>
    <link href="https://example.com/entry-1"/>
    <id>entry-1</id>
    <updated>2025-01-15T12:00:00Z</updated>
    <summary>An atom entry.</summary>
    <author><name>Jane Doe</name></author>
  </entry>
</feed>"""


class TestParseRSS:
    def test_parse_rss_feed_info(self):
        feed_info, entries = parse_feed(RSS_SAMPLE)
        assert feed_info["title"] == "Test RSS Feed"
        assert feed_info["link"] == "https://example.com"

    def test_parse_rss_entries(self):
        _, entries = parse_feed(RSS_SAMPLE)
        assert len(entries) == 2
        assert entries[0]["title"] == "First Post"
        assert entries[0]["guid"] == "post-1"
        assert entries[0]["link"] == "https://example.com/post-1"
        assert entries[0]["summary"] == "This is the first post."
        assert entries[0]["published"] is not None

    def test_parse_rss_dates(self):
        _, entries = parse_feed(RSS_SAMPLE)
        assert entries[0]["published"].year == 2025
        assert entries[0]["published"].month == 1
        assert entries[0]["published"].day == 15


class TestParseAtom:
    def test_parse_atom_feed_info(self):
        feed_info, entries = parse_feed(ATOM_SAMPLE)
        assert feed_info["title"] == "Test Atom Feed"

    def test_parse_atom_entries(self):
        _, entries = parse_feed(ATOM_SAMPLE)
        assert len(entries) == 1
        assert entries[0]["title"] == "Atom Entry"
        assert entries[0]["guid"] == "entry-1"
        assert entries[0]["author"] == "Jane Doe"
        assert entries[0]["summary"] == "An atom entry."
        assert entries[0]["published"] is not None


class TestMalformedFeed:
    def test_malformed_content_raises(self):
        with pytest.raises(FeedError):
            parse_feed("<html><body>Not a feed</body></html>", url="https://bad.com")

    def test_empty_content_raises(self):
        with pytest.raises(FeedError):
            parse_feed("", url="https://empty.com")


class TestEntriesToArticles:
    def test_conversion(self):
        _, entries = parse_feed(RSS_SAMPLE)
        articles = entries_to_articles(entries, feed_id=1)
        assert len(articles) == 2
        assert articles[0].feed_id == 1
        assert articles[0].guid == "post-1"
        assert articles[0].is_read is False
