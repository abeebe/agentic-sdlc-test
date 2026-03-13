## Why

The "add feed" input bar is docked to the bottom of the screen and gets hidden behind the Footer widget, making it unusable. The input needs to be visible and clearly focused when activated.

## What Changes

- Replace the bottom-docked `Input` bar with a centered modal/popover for the add-feed URL prompt
- The popover appears in the center of the screen when `a` is pressed and disappears on submit or Escape

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities
- `tui-feed-management`: The add-feed input changes from a bottom-docked bar to a centered screen popover.

## Impact

- `rss_reader/tui.py` — Replace the `#input-bar` Input widget with a Textual `Screen` or centered container overlay
- No storage or model changes
