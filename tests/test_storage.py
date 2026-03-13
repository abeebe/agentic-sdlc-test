import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from rss_reader.models import Article
from rss_reader.storage import Storage


@pytest.fixture
def storage(tmp_path):
    db_path = tmp_path / "test.db"
    s = Storage(db_path=db_path)
    yield s
    s.close()


class TestFeedCRUD:
    def test_add_feed(self, storage):
        feed = storage.add_feed("Test Feed", "https://example.com/feed.xml", "https://example.com")
        assert feed.id is not None
        assert feed.title == "Test Feed"
        assert feed.url == "https://example.com/feed.xml"

    def test_add_duplicate_feed_url(self, storage):
        storage.add_feed("Feed 1", "https://example.com/feed.xml")
        with pytest.raises(Exception):
            storage.add_feed("Feed 2", "https://example.com/feed.xml")

    def test_list_feeds(self, storage):
        storage.add_feed("Alpha", "https://alpha.com/feed")
        storage.add_feed("Beta", "https://beta.com/feed")
        feeds = storage.list_feeds()
        assert len(feeds) == 2
        assert feeds[0].title == "Alpha"
        assert feeds[1].title == "Beta"

    def test_list_feeds_empty(self, storage):
        feeds = storage.list_feeds()
        assert feeds == []

    def test_remove_feed_by_title(self, storage):
        storage.add_feed("Test Feed", "https://example.com/feed.xml")
        assert storage.remove_feed("Test Feed") is True
        assert storage.list_feeds() == []

    def test_remove_feed_by_id(self, storage):
        feed = storage.add_feed("Test Feed", "https://example.com/feed.xml")
        assert storage.remove_feed(str(feed.id)) is True
        assert storage.list_feeds() == []

    def test_remove_nonexistent_feed(self, storage):
        assert storage.remove_feed("nope") is False

    def test_get_feed_by_name(self, storage):
        storage.add_feed("My Feed", "https://example.com/feed.xml")
        feed = storage.get_feed_by_name("My Feed")
        assert feed is not None
        assert feed.title == "My Feed"

    def test_get_feed_by_name_not_found(self, storage):
        assert storage.get_feed_by_name("nope") is None

    def test_feed_url_exists(self, storage):
        storage.add_feed("Test", "https://example.com/feed.xml")
        assert storage.feed_url_exists("https://example.com/feed.xml") is True
        assert storage.feed_url_exists("https://other.com/feed.xml") is False


class TestArticleCRUD:
    def _make_article(self, feed_id, guid="guid-1", title="Article 1"):
        return Article(
            id=None,
            feed_id=feed_id,
            guid=guid,
            title=title,
            link="https://example.com/article",
            author="Author",
            published=datetime(2025, 1, 15, 12, 0),
            summary="Summary text",
        )

    def test_add_and_get_articles(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        article = self._make_article(feed.id)
        assert storage.add_article(article) is True
        articles = storage.get_articles()
        assert len(articles) == 1
        assert articles[0].title == "Article 1"
        assert articles[0].feed_title == "Feed"

    def test_article_deduplication(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        article = self._make_article(feed.id, guid="same-guid")
        assert storage.add_article(article) is True
        assert storage.add_article(article) is False

    def test_mark_read(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id))
        articles = storage.get_articles()
        assert articles[0].is_read is False
        storage.mark_read(articles[0].id)
        articles = storage.get_articles()
        assert articles[0].is_read is True

    def test_filter_by_feed(self, storage):
        f1 = storage.add_feed("Feed 1", "https://f1.com/feed")
        f2 = storage.add_feed("Feed 2", "https://f2.com/feed")
        storage.add_article(self._make_article(f1.id, guid="a1"))
        storage.add_article(self._make_article(f2.id, guid="a2"))
        articles = storage.get_articles(feed_id=f1.id)
        assert len(articles) == 1
        assert articles[0].feed_title == "Feed 1"

    def test_unread_count_in_feed_list(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id, guid="a1"))
        storage.add_article(self._make_article(feed.id, guid="a2"))
        feeds = storage.list_feeds()
        assert feeds[0].unread_count == 2

    def test_remove_feed_cascades_articles(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id))
        storage.remove_feed("Feed")
        assert storage.get_articles() == []

    def test_delete_article(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id, guid="a1"))
        storage.add_article(self._make_article(feed.id, guid="a2"))
        articles = storage.get_articles()
        assert len(articles) == 2
        storage.delete_article(articles[0].id)
        articles = storage.get_articles()
        assert len(articles) == 1

    def test_toggle_favorite(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id))
        articles = storage.get_articles()
        assert articles[0].is_favorite is False
        storage.toggle_favorite(articles[0].id)
        articles = storage.get_articles()
        assert articles[0].is_favorite is True
        storage.toggle_favorite(articles[0].id)
        articles = storage.get_articles()
        assert articles[0].is_favorite is False

    def test_get_articles_favorites_only(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id, guid="a1"))
        storage.add_article(self._make_article(feed.id, guid="a2"))
        articles = storage.get_articles()
        storage.toggle_favorite(articles[0].id)
        favorites = storage.get_articles(favorites_only=True)
        assert len(favorites) == 1
        assert favorites[0].is_favorite is True

    def test_get_articles_favorites_only_empty(self, storage):
        feed = storage.add_feed("Feed", "https://example.com/feed.xml")
        storage.add_article(self._make_article(feed.id))
        favorites = storage.get_articles(favorites_only=True)
        assert favorites == []
