## Context

The current add-feed input is an `Input` widget docked to the bottom of the screen. It gets occluded by the Footer widget, making it impossible to see what you're typing.

## Goals / Non-Goals

**Goals:**
- Centered modal popover for add-feed URL entry
- Clear visual focus — the modal is obviously the active element
- Escape and submit both dismiss it

**Non-Goals:**
- Changing how remove-feed confirmation works (the confirm bar is fine as-is since it's a single y/n keypress, not text input)

## Decisions

### Use Textual's `Screen` push for the modal

Push a new `ModalScreen` with a centered container holding a title label and the `Input` widget. The screen is popped on submit or Escape. This avoids z-order issues entirely since Textual screens stack above the main content.

Alternatives considered:
- **CSS overlay with high layer**: Works but requires manual focus management and z-index hacks
- **Container with `dock: top` centered**: Still has stacking issues with Footer

## Risks / Trade-offs

- **[Screen push complexity]** Pushing a screen means the modal needs to communicate the result back to the main app → Mitigate by using `dismiss()` with a return value or calling the storage method directly from the modal screen
