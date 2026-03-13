## 1. Project Setup

- [x] 1.1 Create project structure (`rss_reader/` package with `__main__.py`, `cli.py`, `feed.py`, `storage.py`, `models.py`, `tui.py`)
- [x] 1.2 Create `pyproject.toml` with dependencies (click, feedparser, textual, httpx) and `rss` entry point
- [x] 1.3 Set up virtual environment and install dependencies

## 2. Data Models and Storage

- [x] 2.1 Define `Feed` and `Article` dataclasses in `models.py` (id, title, url, link, unread count for feeds; id, feed_id, title, link, author, published, summary, is_read for articles)
- [x] 2.2 Implement SQLite storage layer in `storage.py` (create tables, add/remove/list feeds, add/get/update articles, mark read, filter by feed)
- [x] 2.3 Add article deduplication by guid/id in storage layer

## 3. Feed Fetching and Parsing

- [x] 3.1 Implement feed fetching with httpx in `feed.py` (timeout handling, error handling per feed)
- [x] 3.2 Implement RSS 2.0 and Atom parsing via feedparser (extract title, link, date, summary/content)
- [x] 3.3 Implement fetch-all and fetch-single-feed logic with new article detection and storage

## 4. CLI Commands

- [x] 4.1 Set up Click group and entry point in `cli.py` and `__main__.py`
- [x] 4.2 Implement `rss add <url>` command with `--name` flag (validates feed URL by fetching, rejects duplicates)
- [x] 4.3 Implement `rss remove <name-or-id>` command (deletes feed and associated articles)
- [x] 4.4 Implement `rss list` command (displays table of feeds with name, URL, unread count)
- [x] 4.5 Implement `rss fetch [name]` command (fetch all or specific feed, report results)
- [x] 4.6 Implement `rss read [name]` command (launches TUI, optional feed pre-filter)
- [x] 4.7 Ensure proper exit codes (0 success, non-zero failure) and stderr error output

## 5. TUI Article Reader

- [x] 5.1 Create Textual app scaffold in `tui.py` with article list and detail views
- [x] 5.2 Implement article list view (sorted by date, columns: feed, title, date, unread indicator)
- [x] 5.3 Implement article detail view (title, author, date, body/summary rendered as text)
- [x] 5.4 Implement navigation (select article to open, back key to return to list)
- [x] 5.5 Implement read/unread tracking (mark as read on open, visual distinction in list)
- [x] 5.6 Implement feed filter (select feed to filter, clear filter to show all)

## 6. Testing and Polish

- [x] 6.1 Add unit tests for storage layer (add/remove/list feeds, article CRUD, dedup)
- [x] 6.2 Add unit tests for feed parsing (RSS 2.0, Atom, malformed input)
- [x] 6.3 Add integration tests for CLI commands (add, remove, list, fetch)
- [x] 6.4 Test error handling (invalid URLs, network failures, duplicate feeds, non-existent feeds)
