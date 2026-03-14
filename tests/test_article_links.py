"""Tests for article link parsing and active links in TUI."""

from datetime import datetime
from unittest.mock import patch

import pytest
from textual.widgets import DataTable

from rss_reader.models import Article
from rss_reader.storage import Storage
from rss_reader.tui import ArticleDetail, ArticleLink, RSSReaderApp, html_to_text, parse_article_links


# --- Test parse_article_links ---


class TestParseArticleLinks:
    def test_extracts_links(self):
        html = '<p>Read <a href="https://example.com">this article</a> for more.</p>'
        links = parse_article_links(html)
        assert len(links) == 1
        assert links[0] == ("this article", "https://example.com")

    def test_multiple_links(self):
        html = """
        <p>
            <a href="https://a.com">Link A</a> and
            <a href="https://b.com">Link B</a>
        </p>
        """
        links = parse_article_links(html)
        assert len(links) == 2
        assert links[0][1] == "https://a.com"
        assert links[1][1] == "https://b.com"

    def test_no_links(self):
        html = "<p>Just plain text, no links here.</p>"
        links = parse_article_links(html)
        assert len(links) == 0

    def test_link_without_href_skipped(self):
        html = '<p><a>no href</a> and <a href="">empty href</a></p>'
        links = parse_article_links(html)
        assert len(links) == 0

    def test_link_with_no_text_uses_url(self):
        html = '<a href="https://example.com"></a>'
        links = parse_article_links(html)
        assert len(links) == 1
        assert links[0] == ("https://example.com", "https://example.com")

    def test_malformed_html(self):
        html = "<p>broken <a href='https://x.com'>link<p>more text"
        links = parse_article_links(html)
        # BeautifulSoup should still handle this gracefully
        assert len(links) == 1
        assert links[0][1] == "https://x.com"

    def test_plain_text_input(self):
        links = parse_article_links("Just plain text, no HTML at all")
        assert len(links) == 0


# --- Test html_to_text ---


class TestHtmlToText:
    def test_basic_conversion(self):
        html = "<p>Hello <b>world</b></p>"
        text = html_to_text(html)
        assert "Hello" in text
        assert "world" in text

    def test_preserves_line_breaks(self):
        html = "<p>Line 1</p><p>Line 2</p>"
        text = html_to_text(html)
        assert "Line 1" in text
        assert "Line 2" in text

    def test_plain_text_passthrough(self):
        text = html_to_text("Already plain text")
        assert text == "Already plain text"


# --- Test ArticleLink widget and TUI integration ---


@pytest.fixture
def storage(tmp_path):
    db_path = tmp_path / "test.db"
    s = Storage(db_path=db_path)
    yield s
    s.close()


def _add_article_with_links(storage: Storage) -> Article:
    feed = storage.add_feed("Test Blog", "https://test.com/feed", "https://test.com")
    article = Article(
        id=None,
        feed_id=feed.id,
        guid="article-with-links",
        title="Article With Links",
        link="https://test.com/article",
        author="Author",
        published=datetime(2025, 1, 15, 12, 0),
        summary='<p>Check out <a href="https://example.com">Example</a> and <a href="https://other.com">Other</a>.</p>',
    )
    storage.add_article(article)
    return article


def _add_article_no_links(storage: Storage) -> Article:
    feed = storage.add_feed("Test Blog", "https://test.com/feed", "https://test.com")
    article = Article(
        id=None,
        feed_id=feed.id,
        guid="article-no-links",
        title="Plain Article",
        link="https://test.com/plain",
        author="Author",
        published=datetime(2025, 1, 15, 12, 0),
        summary="<p>Just text, no links here.</p>",
    )
    storage.add_article(article)
    return article


class TestArticleLinkWidget:
    @pytest.mark.asyncio
    async def test_links_rendered_for_article_with_links(self, storage):
        """Article with HTML links should render ArticleLink widgets."""
        _add_article_with_links(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            detail = app.query_one("#article-detail", ArticleDetail)
            links = list(detail.query(ArticleLink))
            assert len(links) == 2

    @pytest.mark.asyncio
    async def test_no_links_for_plain_article(self, storage):
        """Article without HTML links should not render ArticleLink widgets."""
        _add_article_no_links(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            detail = app.query_one("#article-detail", ArticleDetail)
            links = list(detail.query(ArticleLink))
            assert len(links) == 0

    @pytest.mark.asyncio
    async def test_link_opens_browser(self, storage):
        """Pressing enter on a focused link should open the URL in browser."""
        _add_article_with_links(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            detail = app.query_one("#article-detail", ArticleDetail)
            links = list(detail.query(ArticleLink))
            assert len(links) >= 1
            links[0].focus()
            await pilot.pause()
            with patch("rss_reader.tui.webbrowser.open") as mock_open:
                await pilot.press("enter")
                await pilot.pause()
                mock_open.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_links_cleared_on_new_article(self, storage):
        """Selecting a different article should clear old links."""
        feed = storage.add_feed("Blog", "https://blog.com/feed", "https://blog.com")
        storage.add_article(Article(
            id=None, feed_id=feed.id, guid="a1", title="With Links",
            link="https://blog.com/1", author=None, published=datetime(2025, 1, 16),
            summary='<a href="https://x.com">X</a>',
        ))
        storage.add_article(Article(
            id=None, feed_id=feed.id, guid="a2", title="No Links",
            link="https://blog.com/2", author=None, published=datetime(2025, 1, 15),
            summary="Plain text only",
        ))
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            # Select first article (with links)
            await pilot.press("space")
            await pilot.pause()
            detail = app.query_one("#article-detail", ArticleDetail)
            assert len(list(detail.query(ArticleLink))) == 1
            # Move to second article (no links)
            await pilot.press("j")
            await pilot.press("space")
            await pilot.pause()
            assert len(list(detail.query(ArticleLink))) == 0


class TestTUIDiscoveryIntegration:
    @pytest.mark.asyncio
    async def test_add_feed_with_discovery_single_result(self, storage):
        """When discovery finds a single feed, it should be added directly."""
        from rss_reader.discovery import DiscoveredFeed

        discovered = [
            DiscoveredFeed(
                url="https://blog.com/feed.xml", title="Blog Feed", feed_type="atom"
            )
        ]
        feed_info = {"title": "Blog Feed", "link": "https://blog.com"}

        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            with (
                patch("rss_reader.tui.resolve_feed_url", return_value=discovered),
                patch("rss_reader.tui.fetch_and_parse", return_value=(feed_info, [])),
            ):
                await pilot.press("a")
                await pilot.pause()
                from textual.widgets import Input

                modal_input = app.screen.query_one("#add-feed-input", Input)
                modal_input.value = "https://blog.com"
                await pilot.press("enter")
                await pilot.pause()
            feeds = storage.list_feeds()
            assert len(feeds) == 1
            assert feeds[0].title == "Blog Feed"

    @pytest.mark.asyncio
    async def test_add_feed_no_feeds_found(self, storage):
        """When discovery finds nothing, show error message."""
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            with patch("rss_reader.tui.resolve_feed_url", return_value=[]):
                await pilot.press("a")
                await pilot.pause()
                from textual.widgets import Input

                modal_input = app.screen.query_one("#add-feed-input", Input)
                modal_input.value = "https://nofeed.com"
                await pilot.press("enter")
                await pilot.pause()
                from rss_reader.tui import AddFeedScreen

                assert isinstance(app.screen, AddFeedScreen)
                from textual.widgets import Label as Lbl
                hint = app.screen.query_one("#add-feed-hint", Lbl)
                assert "No RSS or Atom feeds found" in str(hint.content)
