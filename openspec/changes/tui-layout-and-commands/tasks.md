## 1. Layout Restructure

- [x] 1.1 Replace the three-column `Horizontal` layout with a left feed list pane + right `Vertical` container holding article list (top, ~40%) and article detail (bottom, ~60%)
- [x] 1.2 Update CSS for the new layout proportions and styling

## 2. Navigation and Selection

- [x] 2.1 Change article selection from Enter to Spacebar (override `on_key` or rebind)
- [x] 2.2 Add vim-style navigation: `j` for cursor down, `k` for cursor up in article list
- [x] 2.3 Ensure arrow keys still work for navigation (Textual default behavior)

## 3. In-App Feed Management

- [x] 3.1 Add `a` keybinding to show an input bar for adding a feed URL
- [x] 3.2 On input submission, validate/fetch/add the feed and refresh the feed list; show error on failure
- [x] 3.3 Add `Escape` to dismiss the input bar without adding
- [x] 3.4 Add `F` (Shift+f) keybinding to fetch all subscribed feeds and refresh the article list
- [x] 3.5 Add `r` keybinding to remove the currently highlighted feed (with confirmation prompt)
- [x] 3.6 Ignore `r` when "All Feeds" or "Favorites" is highlighted

## 4. Testing

- [x] 4.1 Add TUI tests for the new horizontal layout (article list top, detail bottom)
- [x] 4.2 Add TUI tests for spacebar selection and vim navigation (j/k)
- [x] 4.3 Add TUI tests for in-app add feed (valid URL, cancel with Escape)
- [x] 4.4 Add TUI tests for in-app fetch
- [x] 4.5 Add TUI tests for in-app remove feed (confirm, cancel, ignore on non-feed)
