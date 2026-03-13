## Context

The `AddFeedScreen` modal uses `border: thick $accent` which renders as a gold/yellow outline. The rest of the TUI uses `$surface-lighten-2` for its dividers (feed list border, article list/detail split). The modal should visually match.

## Goals / Non-Goals

**Goals:**
- Consistent border color between the modal and the rest of the TUI

**Non-Goals:**
- Changing border thickness or style
- Changing any other modal styling (background, padding, alignment)

## Decisions

### Use `$surface-lighten-2` for the modal border

Change `border: thick $accent` to `border: thick $surface-lighten-2` in `AddFeedScreen.CSS`. This matches the `border-right` and `border-bottom` dividers already used in the main layout.

## Risks / Trade-offs

- **[Reduced contrast]** The dark blue border is more subtle than the gold accent → Acceptable since the modal is already visually distinct via its centered overlay and background
