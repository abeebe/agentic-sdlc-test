from rss_reader.storage import Storage
from rss_reader.tui import RSSReaderApp


def cli():
    """Launch the RSS Reader TUI application."""
    storage = Storage()
    app = RSSReaderApp(storage=storage)
    app.run()
    storage.close()
