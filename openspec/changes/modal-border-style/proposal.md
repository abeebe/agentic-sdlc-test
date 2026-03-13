## Why

The add-feed modal popover uses a gold/accent-colored border (`$accent`) which clashes with the rest of the TUI's visual style. The scrollbar borders use a dark blue (`$surface-lighten-2`) that is more cohesive. The modal border should match.

## What Changes

- Change the `AddFeedScreen` modal dialog border color from `$accent` to `$surface-lighten-2` to match the scrollbar/divider color used elsewhere in the layout

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

_(none — this is a CSS-only styling change with no behavioral requirement changes)_

## Impact

- `rss_reader/tui.py` — One CSS property change in `AddFeedScreen.CSS`
