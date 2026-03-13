## Context

The current TUI uses a `Horizontal` container with three side-by-side panes: feed list (left), article list (center), article detail (right). Long article titles get truncated because the article list and detail compete for horizontal space. Feed management (add/fetch/remove) requires exiting the TUI.

## Goals / Non-Goals

**Goals:**
- Horizontal (top/bottom) split for article list and detail so titles have full width
- Vim-style navigation (j/k) and spacebar article selection
- In-app feed management without leaving the TUI

**Non-Goals:**
- Resizable/draggable pane boundaries
- Full vim modal editing (visual mode, etc.)
- Background/auto-fetch on a timer

## Decisions

### Layout: Left sidebar + right vertical stack

The layout becomes: feed list (left, ~20% width) | right pane with `Vertical` containing article list on top (~40% height) and article detail on bottom (~60% height). This gives article titles the full width of the right side.

Alternatives considered:
- **Keep horizontal split, widen article pane**: Doesn't solve the fundamental space competition

### Navigation: Vim keys via Textual key bindings

Map `j` → cursor down, `k` → cursor up on the `DataTable`. Map `space` to select the current row (show article detail). These are added as Textual `Binding` entries. Arrow keys continue to work via Textual defaults.

### In-app feed management: Textual Input widget in a modal/overlay

Use Textual's `Input` widget for the add-feed URL prompt. Bind `a` to open an input bar at the bottom for the feed URL. Bind `r` to remove the currently selected feed (with confirmation). Bind `F` (shift+f) to fetch all feeds. After add/fetch/remove, refresh the feed list and article list.

Alternatives considered:
- **Separate screen/modal**: Heavier; a simple input bar is more ergonomic for single-field entry
- **Command palette**: Overkill for 3 actions

## Risks / Trade-offs

- **[Keybinding conflicts]** `j`/`k`/`a`/`r` may conflict with text input → Mitigate by only binding these when the input bar is not focused
- **[Feed removal UX]** Accidental `r` could delete a feed → Mitigate with a confirmation prompt before removal
- **[Fetch blocking]** Fetching feeds is synchronous and could freeze the TUI → Acceptable for v1; Textual workers can be added later for async fetch
