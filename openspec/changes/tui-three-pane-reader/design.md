## Context

The current TUI (`tui.py`) uses a single `DataTable` for the article list and toggles visibility between the list and an `ArticleDetail` widget. Feed filtering is done by cycling through feeds with a keybinding. When navigating back from an article, the cursor position is lost because the table is fully rebuilt via `_refresh_articles()`.

## Goals / Non-Goals

**Goals:**
- Three-pane layout: feed list (left sidebar) | article list (center) | article detail (right)
- Direct feed selection by clicking/navigating in the feed pane
- Cursor position preserved in article list when returning from detail view
- Delete article action removes article from storage and list immediately

**Non-Goals:**
- Resizable panes (use fixed proportions for now)
- Batch delete / select-all operations
- Keyboard-driven pane resizing

## Decisions

### Layout: Horizontal container with three panes

Use Textual's `Horizontal` container with three child containers. The feed list pane uses a `ListView` (simpler for a single-column list), the article list uses a `DataTable`, and the detail pane uses the existing `ArticleDetail` scrollable widget. Proportions: ~20% feeds, ~35% articles, ~45% detail.

Alternatives considered:
- **Two-pane with sidebar**: Simpler, but doesn't show the article detail inline — user still has to toggle views
- **Tabs for feeds**: Less discoverable and doesn't show all feeds at once

### Feed filtering: Selection in feed ListView

Selecting a feed in the left pane filters the center article list. An "All Feeds" entry at the top allows clearing the filter. This replaces the `f`/`a` keybinding cycling.

### Cursor retention: Track row index, don't rebuild table

Instead of calling `clear()` + re-adding all rows on every refresh, track the selected row key/index before refresh and restore it after. Use `DataTable.move_cursor(row=idx)` after repopulating.

### Article deletion: `d` keybinding + storage method

Add a `delete_article(article_id)` method to `Storage`. In the TUI, pressing `d` on a highlighted article removes it from storage and from the in-memory list, then adjusts the cursor position (move to next article, or previous if at the end).

### Article favorite: `s` keybinding + storage column

Add an `is_favorite` boolean column to the articles table (default false). Add `toggle_favorite(article_id)` and support a `favorites_only` filter in `get_articles()`. In the TUI, pressing `s` (star) toggles the favorite status. A "Favorites" entry in the feed list pane filters to starred articles. Favorited articles show a star (★) indicator in the article list.

### Pane focus: Tab key to cycle

Use Textual's built-in focus cycling (Tab/Shift+Tab) to move between panes. The currently focused pane gets a visual border highlight.

## Risks / Trade-offs

- **[Layout complexity]** Three-pane layout is harder to render well in narrow terminals → Mitigate with minimum width check and graceful fallback message
- **[Breaking change]** The TUI layout is completely different from v1 → Acceptable since this is an early-stage tool with no external consumers
- **[Focus management]** Textual focus between panes can be tricky → Mitigate by using `can_focus=True` on the right widgets and testing navigation
