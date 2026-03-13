import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from rss_reader.cli import cli
from rss_reader.storage import Storage

RSS_SAMPLE = """<?xml version="1.0" encoding="UTF-8"?>
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


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def tmp_storage(tmp_path):
    """Patch Storage to use a temp database."""
    db_path = tmp_path / "test.db"

    original_init = Storage.__init__

    def patched_init(self, db_path_arg=None):
        original_init(self, db_path=db_path)

    with patch.object(Storage, "__init__", patched_init):
        yield db_path


@pytest.fixture
def mock_fetch():
    """Mock fetch_and_parse to return sample data without network access."""
    feed_info = {"title": "Test Feed", "link": "https://example.com"}
    entries = [
        {
            "guid": "1",
            "title": "Post 1",
            "link": "https://example.com/1",
            "author": None,
            "published": None,
            "summary": "Content",
        }
    ]
    with patch("rss_reader.cli.fetch_and_parse", return_value=(feed_info, entries)) as m:
        yield m


class TestAddCommand:
    def test_add_feed(self, runner, tmp_storage, mock_fetch):
        result = runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        assert result.exit_code == 0
        assert "Added feed: Test Feed" in result.output

    def test_add_feed_custom_name(self, runner, tmp_storage, mock_fetch):
        result = runner.invoke(
            cli, ["add", "https://example.com/feed.xml", "--name", "My Feed"]
        )
        assert result.exit_code == 0
        assert "Added feed: My Feed" in result.output

    def test_add_duplicate_feed(self, runner, tmp_storage, mock_fetch):
        runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        result = runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        assert result.exit_code != 0
        assert "Already subscribed" in result.output


class TestRemoveCommand:
    def test_remove_feed(self, runner, tmp_storage, mock_fetch):
        runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        result = runner.invoke(cli, ["remove", "Test Feed"])
        assert result.exit_code == 0
        assert "Removed feed" in result.output

    def test_remove_nonexistent(self, runner, tmp_storage):
        result = runner.invoke(cli, ["remove", "nope"])
        assert result.exit_code != 0
        assert "not found" in result.output


class TestListCommand:
    def test_list_empty(self, runner, tmp_storage):
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No feeds subscribed" in result.output

    def test_list_feeds(self, runner, tmp_storage, mock_fetch):
        runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Test Feed" in result.output


class TestFetchCommand:
    def test_fetch_all(self, runner, tmp_storage, mock_fetch):
        runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        result = runner.invoke(cli, ["fetch"])
        assert result.exit_code == 0
        assert "new article" in result.output

    def test_fetch_specific(self, runner, tmp_storage, mock_fetch):
        runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        result = runner.invoke(cli, ["fetch", "Test Feed"])
        assert result.exit_code == 0

    def test_fetch_nonexistent(self, runner, tmp_storage):
        result = runner.invoke(cli, ["fetch", "nope"])
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_fetch_no_feeds(self, runner, tmp_storage):
        result = runner.invoke(cli, ["fetch"])
        assert result.exit_code == 0
        assert "No feeds subscribed" in result.output


class TestErrorHandling:
    def test_add_invalid_url(self, runner, tmp_storage):
        from rss_reader.feed import FeedError

        with patch(
            "rss_reader.cli.fetch_and_parse",
            side_effect=FeedError("Network error"),
        ):
            result = runner.invoke(cli, ["add", "https://bad.com/feed"])
            assert result.exit_code != 0
            assert "Error" in result.output

    def test_fetch_with_failing_feed(self, runner, tmp_storage, mock_fetch):
        from rss_reader.feed import FeedError

        runner.invoke(cli, ["add", "https://example.com/feed.xml"])
        with patch(
            "rss_reader.cli.fetch_and_parse",
            side_effect=FeedError("Timeout"),
        ):
            result = runner.invoke(cli, ["fetch"])
            assert "Warning" in result.output
