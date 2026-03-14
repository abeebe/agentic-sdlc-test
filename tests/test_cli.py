"""Tests for the CLI entry point."""

from unittest.mock import patch

from rss_reader.cli import cli
from rss_reader.storage import Storage


class TestCLIEntryPoint:
    def test_cli_function_exists(self):
        """The cli function should exist and be callable."""
        assert callable(cli)

    def test_cli_launches_tui(self, tmp_path):
        """The cli function should launch the TUI app."""
        db_path = tmp_path / "test.db"

        original_init = Storage.__init__

        def patched_init(self, db_path_arg=None):
            original_init(self, db_path=db_path)

        with (
            patch.object(Storage, "__init__", patched_init),
            patch("rss_reader.cli.RSSReaderApp") as mock_app_cls,
        ):
            mock_app = mock_app_cls.return_value
            cli()
            mock_app_cls.assert_called_once()
            mock_app.run.assert_called_once()
