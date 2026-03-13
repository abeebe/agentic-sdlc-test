## Context

This is a greenfield CLI application for aggregating and reading RSS/Atom feeds in the terminal. There is no existing codebase to integrate with. The target users are developers and power users who prefer terminal-based workflows.

## Goals / Non-Goals

**Goals:**
- Provide a fast, ergonomic CLI for managing RSS feed subscriptions
- Support both RSS 2.0 and Atom feed formats
- Offer a TUI (terminal UI) for browsing and reading articles
- Persist subscriptions and read state across sessions
- Follow Unix CLI conventions (flags, exit codes, piping)

**Non-Goals:**
- Full-text content extraction / web scraping (display what the feed provides)
- OPML import/export (future enhancement)
- Background daemon or scheduled fetching (manual fetch only for v1)
- Sync across devices or cloud storage
- Podcast/enclosure playback

## Decisions

### Language: Python

Python provides rapid development, excellent RSS parsing libraries (`feedparser`), and mature TUI frameworks. The target audience likely has Python installed. Alternatives considered:
- **Go**: Better for distributing single binaries, but slower development for TUI work
- **Rust**: Best performance, but higher development cost for a tool of this scope

### TUI Framework: Textual

Textual provides a modern, rich TUI experience with built-in widgets for lists, scrolling, and layout. Alternatives considered:
- **curses**: Too low-level, significant boilerplate
- **Rich + prompt_toolkit**: Good but less cohesive for full-app TUI

### Storage: SQLite via sqlite3

SQLite is zero-config, file-based, and handles concurrent reads well. Stores feeds, articles, and read state. Alternatives considered:
- **JSON flat file**: Simpler but doesn't scale well with many articles and lacks query capability
- **TinyDB**: Extra dependency for limited benefit over raw SQLite

### Feed Parsing: feedparser

The `feedparser` library is the de facto standard for RSS/Atom parsing in Python — handles edge cases, encoding issues, and malformed feeds. No serious alternatives exist in the Python ecosystem.

### CLI Framework: Click

Click provides decorator-based command definitions, automatic help generation, and good composability. Alternatives considered:
- **argparse**: Standard library but verbose for multi-command CLIs
- **Typer**: Nice but adds a dependency on Click anyway plus Pydantic

### Architecture

```
rss_reader/
├── __main__.py       # Entry point
├── cli.py            # Click command definitions
├── tui.py            # Textual TUI app
├── feed.py           # Feed fetching and parsing
├── storage.py        # SQLite database layer
└── models.py         # Data classes (Feed, Article)
```

The CLI layer (`cli.py`) handles command dispatch. Non-interactive commands (add, remove, list, fetch) execute directly. The `read` command launches the TUI app. The storage layer abstracts all database access behind a simple API.

## Risks / Trade-offs

- **[Python dependency]** Users need Python 3.10+ installed → Mitigate by documenting requirements and supporting `pipx install`
- **[Textual compatibility]** Textual requires a modern terminal emulator → Mitigate by gracefully degrading or warning on unsupported terminals
- **[Feed variety]** RSS feeds vary wildly in quality and format → Mitigate by relying on feedparser's battle-tested parsing and handling errors per-feed rather than failing globally
- **[Storage growth]** SQLite database could grow large with many feeds over time → Mitigate by adding a configurable article retention limit (default: 500 per feed)
