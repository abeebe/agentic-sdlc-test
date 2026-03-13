import sys

import click

from rss_reader.feed import FeedError, entries_to_articles, fetch_and_parse
from rss_reader.storage import Storage


@click.group()
def cli():
    """A CLI-based RSS feed aggregator and reader."""
    pass


@cli.command()
@click.argument("url")
@click.option("--name", default=None, help="Custom display name for the feed.")
def add(url: str, name: str | None):
    """Subscribe to an RSS/Atom feed."""
    storage = Storage()
    try:
        if storage.feed_url_exists(url):
            click.echo(f"Error: Already subscribed to {url}", err=True)
            sys.exit(1)

        feed_info, _ = fetch_and_parse(url)
        title = name or feed_info["title"]
        storage.add_feed(title=title, url=url, link=feed_info.get("link", ""))
        click.echo(f"Added feed: {title}")
    except FeedError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        storage.close()


@cli.command()
@click.argument("identifier")
def remove(identifier: str):
    """Unsubscribe from a feed by name or ID."""
    storage = Storage()
    try:
        if storage.remove_feed(identifier):
            click.echo(f"Removed feed: {identifier}")
        else:
            click.echo(f"Error: Feed not found: {identifier}", err=True)
            sys.exit(1)
    finally:
        storage.close()


@cli.command("list")
def list_feeds():
    """List all subscribed feeds."""
    storage = Storage()
    try:
        feeds = storage.list_feeds()
        if not feeds:
            click.echo("No feeds subscribed. Use 'rss add <url>' to add one.")
            return
        # Print table
        name_width = max(len(f.title) for f in feeds)
        name_width = max(name_width, 4)
        click.echo(f"{'Name':<{name_width}}  {'URL':<50}  Unread")
        click.echo(f"{'─' * name_width}  {'─' * 50}  ──────")
        for feed in feeds:
            click.echo(
                f"{feed.title:<{name_width}}  {feed.url:<50}  {feed.unread_count}"
            )
    finally:
        storage.close()


@cli.command()
@click.argument("name", required=False)
def fetch(name: str | None):
    """Fetch updates from all feeds, or a specific feed by name."""
    storage = Storage()
    try:
        if name:
            feed = storage.get_feed_by_name(name)
            if not feed:
                click.echo(f"Error: Feed not found: {name}", err=True)
                sys.exit(1)
            feeds = [feed]
        else:
            feeds = storage.list_feeds()
            if not feeds:
                click.echo("No feeds subscribed. Use 'rss add <url>' to add one.")
                return

        total_new = 0
        for feed in feeds:
            try:
                _, entries = fetch_and_parse(feed.url)
                articles = entries_to_articles(entries, feed.id)
                new_count = sum(1 for a in articles if storage.add_article(a))
                total_new += new_count
                click.echo(f"  {feed.title}: {new_count} new article(s)")
            except FeedError as e:
                click.echo(f"  Warning: {feed.title}: {e}", err=True)

        if total_new == 0:
            click.echo("All feeds are up to date.")
        else:
            click.echo(f"Fetched {total_new} new article(s) total.")
    finally:
        storage.close()


@cli.command()
@click.argument("name", required=False)
def read(name: str | None):
    """Launch the interactive TUI article reader."""
    from rss_reader.tui import RSSReaderApp

    storage = Storage()
    feed_filter = None
    if name:
        feed = storage.get_feed_by_name(name)
        if not feed:
            click.echo(f"Error: Feed not found: {name}", err=True)
            storage.close()
            sys.exit(1)
        feed_filter = feed.id

    app = RSSReaderApp(storage=storage, feed_filter=feed_filter)
    app.run()
    storage.close()
