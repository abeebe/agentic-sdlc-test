from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from rss_reader.feed import FeedError, entries_to_articles, fetch_and_parse
from rss_reader.models import Article
from rss_reader.storage import Storage

FILTER_ALL = "all"
FILTER_FAVORITES = "favorites"


class AddFeedScreen(ModalScreen[Optional[str]]):
    """Modal screen for adding a feed URL."""

    CSS = """
    AddFeedScreen {
        align: center middle;
    }
    #add-feed-dialog {
        width: 60;
        height: auto;
        max-height: 10;
        border: thick $surface-lighten-2;
        background: $surface;
        padding: 1 2;
    }
    #add-feed-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #add-feed-input {
        margin-bottom: 1;
    }
    #add-feed-hint {
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage

    def compose(self) -> ComposeResult:
        with Vertical(id="add-feed-dialog"):
            yield Label("Add Feed", id="add-feed-title")
            yield Input(placeholder="Enter feed URL...", id="add-feed-input")
            yield Label("Enter to submit, Escape to cancel", id="add-feed-hint")

    def on_mount(self):
        self.query_one("#add-feed-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted):
        url = event.value.strip()
        if not url:
            self.dismiss(None)
            return
        try:
            feed_info, _ = fetch_and_parse(url)
            if self.storage.feed_url_exists(url):
                self.query_one("#add-feed-hint", Label).update(
                    f"Error: Already subscribed to {url}"
                )
                return
            self.storage.add_feed(
                title=feed_info["title"], url=url, link=feed_info.get("link", "")
            )
            self.dismiss(feed_info["title"])
        except FeedError as e:
            self.query_one("#add-feed-hint", Label).update(f"Error: {e}")

    def action_cancel(self):
        self.dismiss(None)


class ArticleDetail(VerticalScroll):
    """Displays a single article's content."""

    def compose(self) -> ComposeResult:
        yield Label("Select an article to read", id="article-title")
        yield Label("", id="article-meta")
        yield Static("", id="article-body")

    def show_article(self, article: Article):
        self.query_one("#article-title", Label).update(article.title)
        meta_parts = []
        if article.feed_title:
            meta_parts.append(article.feed_title)
        if article.author:
            meta_parts.append(article.author)
        if article.published:
            meta_parts.append(article.published.strftime("%Y-%m-%d %H:%M"))
        self.query_one("#article-meta", Label).update(" | ".join(meta_parts))
        self.query_one("#article-body", Static).update(article.summary or "(no content)")
        self.scroll_home(animate=False)

    def clear_detail(self):
        self.query_one("#article-title", Label).update("Select an article to read")
        self.query_one("#article-meta", Label).update("")
        self.query_one("#article-body", Static).update("")


class RSSReaderApp(App):
    """TUI RSS Reader with two-column layout."""

    TITLE = "RSS Reader"
    CSS = """
    #main-container {
        height: 1fr;
    }
    #feed-list {
        width: 20%;
        min-width: 20;
        border-right: solid $surface-lighten-2;
    }
    #feed-list > ListItem {
        padding: 0 1;
    }
    #right-pane {
        width: 80%;
    }
    #article-list-pane {
        height: 40%;
        border-bottom: solid $surface-lighten-2;
    }
    #article-detail {
        height: 60%;
        padding: 1 2;
    }
    #article-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #article-meta {
        color: $text-muted;
        margin-bottom: 1;
    }
    #article-body {
        margin-top: 1;
    }
    #status-bar {
        height: 1;
        dock: bottom;
        background: $surface;
        padding: 0 1;
    }
    #confirm-bar {
        height: 1;
        dock: bottom;
        display: none;
        background: $error;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "delete", "Delete Article"),
        Binding("s", "star", "Star"),
        Binding("a", "add_feed", "Add Feed"),
        Binding("F", "fetch_feeds", "Fetch"),
        Binding("r", "remove_feed", "Remove Feed"),
        Binding("j", "vim_down", "Down", show=False),
        Binding("k", "vim_up", "Up", show=False),
        Binding("space", "select_article", "Select", show=False),
    ]

    def __init__(self, storage: Storage, feed_filter: Optional[int] = None):
        super().__init__()
        self.storage = storage
        self.feed_filter: str | int | None = feed_filter
        self.articles: list[Article] = []
        self.current_article: Optional[Article] = None
        self.feeds = []
        self._saved_cursor_row: int = 0
        self._input_mode: Optional[str] = None  # "confirm_remove" only now
        self._pending_remove_feed = None
        # Maps feed list index -> filter value
        self._feed_list_map: list[str | int] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield ListView(id="feed-list")
            with Vertical(id="right-pane"):
                yield DataTable(id="article-list-pane")
                yield ArticleDetail(id="article-detail")
        yield Label("", id="status-bar")
        yield Label("", id="confirm-bar")
        yield Footer()

    def on_mount(self):
        self._rebuild_feed_list()
        table = self.query_one("#article-list-pane", DataTable)
        table.cursor_type = "row"
        table.add_columns("", "★", "Feed", "Title", "Date")
        self._refresh_articles()

        # If a feed_filter was passed from CLI, select it in the feed list
        if self.feed_filter is not None:
            feed_list = self.query_one("#feed-list", ListView)
            for i, filter_val in enumerate(self._feed_list_map):
                if filter_val == self.feed_filter:
                    feed_list.index = i
                    break

    def _rebuild_feed_list(self):
        """Build the feed list. Only called on mount."""
        self.feeds = self.storage.list_feeds()
        feed_list = self.query_one("#feed-list", ListView)
        self._feed_list_map = [FILTER_ALL, FILTER_FAVORITES]
        feed_list.append(ListItem(Label("All Feeds")))
        feed_list.append(ListItem(Label("★ Favorites")))
        for feed in self.feeds:
            self._feed_list_map.append(feed.id)
            feed_list.append(ListItem(Label(f"{feed.title} ({feed.unread_count})")))

    async def _refresh_feed_list(self):
        """Refresh feed list content (after add/remove/fetch)."""
        self.feeds = self.storage.list_feeds()
        feed_list = self.query_one("#feed-list", ListView)
        await feed_list.clear()
        self._feed_list_map = [FILTER_ALL, FILTER_FAVORITES]
        feed_list.append(ListItem(Label("All Feeds")))
        feed_list.append(ListItem(Label("★ Favorites")))
        for feed in self.feeds:
            self._feed_list_map.append(feed.id)
            feed_list.append(ListItem(Label(f"{feed.title} ({feed.unread_count})")))

    def _refresh_articles(self, restore_cursor: bool = False):
        table = self.query_one("#article-list-pane", DataTable)

        # Save cursor position
        if restore_cursor:
            saved_row = self._saved_cursor_row
        else:
            saved_row = table.cursor_row if self.articles else 0

        # Determine query params
        feed_id = None
        favorites_only = False
        if self.feed_filter == FILTER_FAVORITES:
            favorites_only = True
        elif isinstance(self.feed_filter, int):
            feed_id = self.feed_filter

        self.articles = self.storage.get_articles(
            feed_id=feed_id, favorites_only=favorites_only
        )
        table.clear()
        if not self.articles:
            table.add_row("", "", "", "No articles available.", "")
            return

        for article in self.articles:
            unread = "●" if not article.is_read else " "
            star = "★" if article.is_favorite else " "
            date_str = (
                article.published.strftime("%Y-%m-%d")
                if article.published
                else ""
            )
            table.add_row(
                unread,
                star,
                article.feed_title or "",
                article.title,
                date_str,
            )

        # Restore cursor position
        target_row = min(saved_row, len(self.articles) - 1)
        if target_row >= 0:
            table.move_cursor(row=target_row)

    def _show_status(self, message: str):
        self.query_one("#status-bar", Label).update(message)

    def _select_current_article(self):
        """Select the article at the current cursor position."""
        table = self.query_one("#article-list-pane", DataTable)
        row = table.cursor_row
        if not self.articles or row >= len(self.articles):
            return
        article = self.articles[row]
        self.current_article = article
        self._saved_cursor_row = row

        if not article.is_read and article.id is not None:
            self.storage.mark_read(article.id)
            article.is_read = True
            self._refresh_articles(restore_cursor=True)

        detail = self.query_one("#article-detail", ArticleDetail)
        detail.show_article(article)

    def on_list_view_selected(self, event: ListView.Selected):
        """Handle feed list selection to filter articles."""
        feed_list = self.query_one("#feed-list", ListView)
        idx = feed_list.index
        if idx is not None and 0 <= idx < len(self._feed_list_map):
            self.feed_filter = self._feed_list_map[idx]
            self._refresh_articles()

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """Handle Enter on article list."""
        self._select_current_article()

    # --- Vim navigation ---

    def action_vim_down(self):
        if self._input_mode:
            return
        table = self.query_one("#article-list-pane", DataTable)
        feed_list = self.query_one("#feed-list", ListView)
        if table.has_focus:
            table.action_cursor_down()
        elif feed_list.has_focus:
            feed_list.action_cursor_down()

    def action_vim_up(self):
        if self._input_mode:
            return
        table = self.query_one("#article-list-pane", DataTable)
        feed_list = self.query_one("#feed-list", ListView)
        if table.has_focus:
            table.action_cursor_up()
        elif feed_list.has_focus:
            feed_list.action_cursor_up()

    def action_select_article(self):
        if self._input_mode:
            return
        table = self.query_one("#article-list-pane", DataTable)
        if table.has_focus:
            self._select_current_article()

    # --- Article actions ---

    def action_delete(self):
        """Delete the highlighted article."""
        if self._input_mode:
            return
        table = self.query_one("#article-list-pane", DataTable)
        row = table.cursor_row
        if not self.articles or row >= len(self.articles):
            return
        article = self.articles[row]
        if article.id is not None:
            self.storage.delete_article(article.id)

        if self.current_article and self.current_article.id == article.id:
            self.current_article = None
            self.query_one("#article-detail", ArticleDetail).clear_detail()

        self._saved_cursor_row = min(row, len(self.articles) - 2) if len(self.articles) > 1 else 0
        self._refresh_articles(restore_cursor=True)

    def action_star(self):
        """Toggle favorite on the highlighted article."""
        if self._input_mode:
            return
        table = self.query_one("#article-list-pane", DataTable)
        row = table.cursor_row
        if not self.articles or row >= len(self.articles):
            return
        article = self.articles[row]
        if article.id is not None:
            self.storage.toggle_favorite(article.id)
            article.is_favorite = not article.is_favorite
        self._saved_cursor_row = row
        self._refresh_articles(restore_cursor=True)

    # --- In-app feed management ---

    def action_add_feed(self):
        """Push modal screen for adding a feed URL."""
        if self._input_mode:
            return
        self.push_screen(AddFeedScreen(self.storage), self._on_add_feed_dismiss)

    def _on_add_feed_dismiss(self, result: Optional[str]) -> None:
        """Called when the add feed modal is dismissed."""
        if result:
            self._show_status(f"Added feed: {result}")
            self.call_after_refresh(self._async_refresh_feed_list)

    async def _async_refresh_feed_list(self):
        await self._refresh_feed_list()

    def on_key(self, event) -> None:
        """Handle keys during confirm mode only."""
        if self._input_mode == "confirm_remove":
            if event.key == "y":
                self._do_remove_feed()
            elif event.key in ("n", "escape"):
                self._dismiss_confirm()
            event.prevent_default()
            event.stop()

    def action_fetch_feeds(self):
        """Fetch all subscribed feeds."""
        if self._input_mode:
            return
        feeds = self.storage.list_feeds()
        if not feeds:
            self._show_status("No feeds subscribed. Press 'a' to add one.")
            return

        total_new = 0
        errors = 0
        for feed in feeds:
            try:
                _, entries = fetch_and_parse(feed.url)
                articles = entries_to_articles(entries, feed.id)
                new_count = sum(1 for a in articles if self.storage.add_article(a))
                total_new += new_count
            except FeedError:
                errors += 1

        self.call_after_refresh(self._async_refresh_feed_list)
        self._refresh_articles(restore_cursor=True)
        msg = f"Fetched {total_new} new article(s)"
        if errors:
            msg += f" ({errors} feed(s) failed)"
        self._show_status(msg)

    def action_remove_feed(self):
        """Remove the currently highlighted feed (with confirmation)."""
        if self._input_mode:
            return
        feed_list = self.query_one("#feed-list", ListView)
        idx = feed_list.index
        if idx is None or idx >= len(self._feed_list_map):
            return
        filter_val = self._feed_list_map[idx]
        # Ignore if on All Feeds or Favorites
        if filter_val in (FILTER_ALL, FILTER_FAVORITES):
            return

        feed = next((f for f in self.feeds if f.id == filter_val), None)
        if not feed:
            return

        self._pending_remove_feed = feed
        self._input_mode = "confirm_remove"
        confirm_bar = self.query_one("#confirm-bar", Label)
        confirm_bar.update(f"Remove '{feed.title}' and all its articles? (y/n)")
        confirm_bar.display = True

    def _do_remove_feed(self):
        feed = self._pending_remove_feed
        self.storage.remove_feed(feed.title)
        self._dismiss_confirm()
        if self.feed_filter == feed.id:
            self.feed_filter = FILTER_ALL
        self.call_after_refresh(self._async_refresh_feed_list)
        self._refresh_articles()
        self._show_status(f"Removed feed: {feed.title}")

    def _dismiss_confirm(self):
        self._input_mode = None
        self._pending_remove_feed = None
        self.query_one("#confirm-bar", Label).display = False
