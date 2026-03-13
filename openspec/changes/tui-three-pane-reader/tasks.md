## 1. Storage Layer Updates

- [x] 1.1 Add `delete_article(article_id)` method to `Storage`
- [x] 1.2 Add `is_favorite` column to articles table (default false, with migration for existing DBs)
- [x] 1.3 Add `toggle_favorite(article_id)` method to `Storage`
- [x] 1.4 Add `favorites_only` parameter to `get_articles()` query
- [x] 1.5 Add `is_favorite` field to `Article` dataclass in `models.py`

## 2. Three-Pane TUI Layout

- [x] 2.1 Replace single-pane layout with `Horizontal` container holding three panes: feed list (left), article list (center), article detail (right)
- [x] 2.2 Create feed list pane using `ListView` with "All Feeds", "Favorites", and each subscribed feed as entries
- [x] 2.3 Wire feed list selection to filter the article list in the center pane
- [x] 2.4 Update CSS for three-pane proportions (~20% / ~35% / ~45%) and pane styling

## 3. Cursor Retention

- [x] 3.1 Track the selected article row index before refreshing the article list
- [x] 3.2 Restore cursor position after article list refresh using `DataTable.move_cursor()`

## 4. Article Delete

- [x] 4.1 Add `d` keybinding to delete the highlighted article from storage and the list
- [x] 4.2 Adjust cursor position after deletion (next article, or previous if at end)

## 5. Article Favorite

- [x] 5.1 Add `s` keybinding to toggle favorite on the highlighted article
- [x] 5.2 Display star indicator (★) in article list for favorited articles
- [x] 5.3 Wire "Favorites" feed list entry to filter `get_articles(favorites_only=True)`

## 6. Navigation and Focus

- [x] 6.1 Remove old `f`/`a` filter keybindings and single-pane toggle logic
- [x] 6.2 Ensure Tab/Shift+Tab cycles focus between feed list, article list, and detail panes
- [x] 6.3 Show article detail in right pane on article selection (no more visibility toggle)

## 7. Testing

- [x] 7.1 Add unit tests for `delete_article` and `toggle_favorite` in storage
- [x] 7.2 Add unit tests for `get_articles(favorites_only=True)` filtering
- [x] 7.3 Update existing TUI-related tests if any break due to layout changes
