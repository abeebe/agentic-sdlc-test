"""Tests for the TUI reader.

These tests use Textual's async test pilot to actually run the app
and verify behavior.
"""

from datetime import datetime
from unittest.mock import patch

import pytest
from textual.containers import Vertical
from textual.widgets import DataTable, Input, Label, ListView

from rss_reader.models import Article
from rss_reader.storage import Storage
from rss_reader.tui import AddFeedScreen, RSSReaderApp


@pytest.fixture
def storage(tmp_path):
    db_path = tmp_path / "test.db"
    s = Storage(db_path=db_path)
    yield s
    s.close()


def _add_test_data(storage: Storage):
    """Add two feeds with articles for testing."""
    f1 = storage.add_feed("Alpha Blog", "https://alpha.com/feed", "https://alpha.com")
    f2 = storage.add_feed("Beta News", "https://beta.com/feed", "https://beta.com")
    for i in range(3):
        storage.add_article(Article(
            id=None,
            feed_id=f1.id,
            guid=f"alpha-{i}",
            title=f"Alpha Article {i}",
            link=f"https://alpha.com/{i}",
            author="Alice",
            published=datetime(2025, 1, 15 + i, 12, 0),
            summary=f"Alpha content {i}",
        ))
    for i in range(2):
        storage.add_article(Article(
            id=None,
            feed_id=f2.id,
            guid=f"beta-{i}",
            title=f"Beta Article {i}",
            link=f"https://beta.com/{i}",
            author="Bob",
            published=datetime(2025, 1, 20 + i, 12, 0),
            summary=f"Beta content {i}",
        ))
    return f1, f2


class TestTUIImportAndLaunch:
    def test_tui_module_imports(self):
        """The TUI module must import without errors."""
        from rss_reader.tui import RSSReaderApp, ArticleDetail
        assert RSSReaderApp is not None
        assert ArticleDetail is not None

    @pytest.mark.asyncio
    async def test_app_launches_empty(self, storage):
        """App should launch and show empty state with no articles."""
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            assert table is not None
            feed_list = app.query_one(ListView)
            assert feed_list is not None

    @pytest.mark.asyncio
    async def test_app_launches_with_articles(self, storage):
        """App should show articles when data exists."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            assert table.row_count == 5


class TestHorizontalLayout:
    @pytest.mark.asyncio
    async def test_right_pane_is_vertical_container(self, storage):
        """Right pane should be a Vertical container (top/bottom split)."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            right_pane = app.query_one("#right-pane", Vertical)
            assert right_pane is not None

    @pytest.mark.asyncio
    async def test_article_list_and_detail_in_right_pane(self, storage):
        """Article list and detail should both be inside the right pane."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            right_pane = app.query_one("#right-pane", Vertical)
            article_list = right_pane.query_one("#article-list-pane", DataTable)
            article_detail = right_pane.query_one("#article-detail")
            assert article_list is not None
            assert article_detail is not None


class TestFeedFiltering:
    @pytest.mark.asyncio
    async def test_feed_list_has_all_and_favorites(self, storage):
        """Feed list should have 'All Feeds', 'Favorites', and feed entries."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            # "All Feeds" + "Favorites" + 2 feeds = 4 entries
            assert len(feed_list.children) == 4

    @pytest.mark.asyncio
    async def test_selecting_feed_filters_articles(self, storage):
        """Selecting a feed in the list should filter articles."""
        f1, f2 = _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            feed_list.index = 2  # First real feed (Alpha Blog)
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            table = app.query_one(DataTable)
            # Alpha Blog has 3 articles
            assert table.row_count == 3

    @pytest.mark.asyncio
    async def test_selecting_all_feeds_shows_everything(self, storage):
        """Selecting 'All Feeds' should show all articles."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            # First filter to a feed
            feed_list.index = 2
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            # Then go back to All Feeds
            feed_list.index = 0
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 5


class TestSpacebarSelection:
    @pytest.mark.asyncio
    async def test_spacebar_selects_article(self, storage):
        """Pressing spacebar should select the highlighted article."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            assert app.current_article is not None

    @pytest.mark.asyncio
    async def test_spacebar_marks_read(self, storage):
        """Selecting with spacebar should mark article as read."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("space")
            await pilot.pause()
            articles = storage.get_articles()
            read_articles = [a for a in articles if a.is_read]
            assert len(read_articles) >= 1


class TestVimNavigation:
    @pytest.mark.asyncio
    async def test_j_moves_down(self, storage):
        """Pressing j should move cursor down."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            assert table.cursor_row == 0
            await pilot.press("j")
            await pilot.pause()
            assert table.cursor_row == 1

    @pytest.mark.asyncio
    async def test_k_moves_up(self, storage):
        """Pressing k should move cursor up."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("j")
            await pilot.press("j")
            await pilot.pause()
            assert table.cursor_row == 2
            await pilot.press("k")
            await pilot.pause()
            assert table.cursor_row == 1

    @pytest.mark.asyncio
    async def test_arrow_keys_still_work(self, storage):
        """Arrow keys should still navigate."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("down")
            await pilot.pause()
            assert table.cursor_row == 1
            await pilot.press("up")
            await pilot.pause()
            assert table.cursor_row == 0


class TestArticleDelete:
    @pytest.mark.asyncio
    async def test_delete_article(self, storage):
        """Pressing 'd' should delete the highlighted article."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("d")
            await pilot.pause()
            assert table.row_count == 4
            assert len(storage.get_articles()) == 4


class TestArticleFavorite:
    @pytest.mark.asyncio
    async def test_toggle_favorite(self, storage):
        """Pressing 's' should toggle the favorite status."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("s")
            await pilot.pause()
            favorited = [a for a in storage.get_articles() if a.is_favorite]
            assert len(favorited) == 1

    @pytest.mark.asyncio
    async def test_favorites_filter(self, storage):
        """Selecting 'Favorites' should show only starred articles."""
        _add_test_data(storage)
        articles = storage.get_articles()
        storage.toggle_favorite(articles[0].id)

        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            feed_list.index = 1  # "Favorites"
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 1


class TestInAppAddFeed:
    @pytest.mark.asyncio
    async def test_add_feed_shows_modal(self, storage):
        """Pressing 'a' should push the AddFeedScreen modal."""
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("a")
            await pilot.pause()
            assert isinstance(app.screen, AddFeedScreen)

    @pytest.mark.asyncio
    async def test_add_feed_escape_dismisses(self, storage):
        """Pressing Escape should dismiss the modal."""
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("a")
            await pilot.pause()
            assert isinstance(app.screen, AddFeedScreen)
            await pilot.press("escape")
            await pilot.pause()
            assert not isinstance(app.screen, AddFeedScreen)

    @pytest.mark.asyncio
    async def test_add_feed_valid_url(self, storage):
        """Submitting a valid URL should add the feed."""
        feed_info = {"title": "New Feed", "link": "https://new.com"}
        entries = []
        # resolve_feed_url returns a tuple for direct feed URLs
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            with patch(
                "rss_reader.tui.resolve_feed_url",
                return_value=("https://new.com/feed.xml", feed_info, entries),
            ):
                await pilot.press("a")
                await pilot.pause()
                modal_input = app.screen.query_one("#add-feed-input", Input)
                modal_input.value = "https://new.com/feed.xml"
                await pilot.press("enter")
                await pilot.pause()
            feeds = storage.list_feeds()
            assert len(feeds) == 1
            assert feeds[0].title == "New Feed"


class TestInAppFetch:
    @pytest.mark.asyncio
    async def test_fetch_feeds(self, storage):
        """Pressing 'F' should fetch all feeds."""
        f1, _ = _add_test_data(storage)
        # Remove all articles to test fetching
        for a in storage.get_articles():
            storage.delete_article(a.id)

        feed_info = {"title": "Alpha Blog", "link": "https://alpha.com"}
        entries = [{
            "guid": "new-1",
            "title": "New Article",
            "link": "https://alpha.com/new",
            "author": None,
            "published": None,
            "summary": "New content",
        }]

        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            with patch("rss_reader.tui.fetch_and_parse", return_value=(feed_info, entries)):
                await pilot.press("F")
                await pilot.pause()
            assert len(storage.get_articles()) > 0

    @pytest.mark.asyncio
    async def test_fetch_no_feeds(self, storage):
        """Pressing 'F' with no feeds should not crash."""
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("F")
            await pilot.pause()
            # Should not crash


class TestInAppRemoveFeed:
    @pytest.mark.asyncio
    async def test_remove_feed_confirm(self, storage):
        """Pressing 'r' on a feed and confirming should remove it."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            feed_list.index = 2  # First real feed
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert app._input_mode == "confirm_remove"
            await pilot.press("y")
            await pilot.pause()
            assert len(storage.list_feeds()) == 1

    @pytest.mark.asyncio
    async def test_remove_feed_cancel(self, storage):
        """Pressing 'r' then 'n' should cancel removal."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            feed_list.index = 2
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            assert app._input_mode is None
            assert len(storage.list_feeds()) == 2

    @pytest.mark.asyncio
    async def test_remove_on_all_feeds_ignored(self, storage):
        """Pressing 'r' on 'All Feeds' should do nothing."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            feed_list.index = 0  # "All Feeds"
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert app._input_mode is None
            assert len(storage.list_feeds()) == 2

    @pytest.mark.asyncio
    async def test_remove_on_favorites_ignored(self, storage):
        """Pressing 'r' on 'Favorites' should do nothing."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            feed_list = app.query_one(ListView)
            feed_list.focus()
            feed_list.index = 1  # "Favorites"
            await pilot.pause()
            await pilot.press("r")
            await pilot.pause()
            assert app._input_mode is None
            assert len(storage.list_feeds()) == 2


class TestCursorRetention:
    @pytest.mark.asyncio
    async def test_cursor_retained_after_star(self, storage):
        """Cursor should stay on the same row after toggling favorite."""
        _add_test_data(storage)
        app = RSSReaderApp(storage=storage)
        async with app.run_test() as pilot:
            table = app.query_one(DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("j")
            await pilot.press("j")
            await pilot.pause()
            assert table.cursor_row == 2
            await pilot.press("s")
            await pilot.pause()
            assert table.cursor_row == 2
