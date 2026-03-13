## Why

The current TUI reader uses a single-pane view that toggles between article list and detail. Browsing articles from a specific feed requires cycling through a filter keybinding, and navigating back from an article loses the cursor position — making it tedious to triage a feed. Users also have no way to remove articles they've finished with, so the list grows unboundedly.

## What Changes

- **BREAKING** Replace the single-pane TUI layout with a three-pane layout: feed list (left), article list (center), article detail (right)
- Selecting a feed in the left pane filters the article list in the center pane
- Retain cursor/highlight position in the article list when returning from article detail view
- Add an article delete action that removes the article from storage and the list
- Add a favorite/star action to bookmark articles for later reading

## Capabilities

### New Capabilities
- `article-delete`: Allow users to delete individual articles from the reader, removing them from storage permanently.
- `article-favorite`: Allow users to star/favorite articles to save them for later. Favorites are visually indicated and can be filtered to.

### Modified Capabilities
- `article-reader`: Layout changes from single-pane toggle to three-pane (feed list | article list | article detail). Feed filtering moves from a keybinding cycle to direct selection in the feed pane. Cursor position is preserved when navigating back from article detail.

## Impact

- `rss_reader/tui.py` — Major rewrite of the TUI layout and navigation
- `rss_reader/storage.py` — New methods to delete and favorite/unfavorite articles; new `is_favorite` column on articles table
- No dependency changes; Textual already supports multi-pane layouts
