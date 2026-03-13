## Why

The current three-pane layout splits the article list and detail side-by-side vertically, which truncates long article titles. Navigation requires Enter to select and lacks vim-style keybindings. Managing feeds (add, fetch, remove) requires exiting the TUI and using separate CLI commands, breaking the reading flow.

## What Changes

- **BREAKING** Change the right side of the three-pane layout from a vertical split to a horizontal split: article list on top (~40%), article detail on bottom (~60%)
- Change article selection from Enter to Spacebar
- Add vim-style navigation (j/k for up/down) in addition to arrow keys
- Add in-app feed management: add a feed (prompts for URL), fetch all feeds, remove a feed — all without leaving the TUI

## Capabilities

### New Capabilities
- `tui-feed-management`: In-app commands to add, fetch, and remove feeds from within the TUI without exiting the application.

### Modified Capabilities
- `article-reader`: Layout changes from vertical to horizontal split on the right side. Article selection key changes from Enter to Spacebar. Vim-style navigation (j/k) added alongside arrow keys.

## Impact

- `rss_reader/tui.py` — Layout restructure and new keybindings/input handling
- `rss_reader/cli.py` — No changes; existing CLI commands remain as-is
- No new dependencies
