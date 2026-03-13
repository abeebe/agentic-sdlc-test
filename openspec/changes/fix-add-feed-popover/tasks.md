## 1. Add Feed Modal

- [x] 1.1 Create an `AddFeedScreen` modal screen class with a centered container, title label, and Input widget
- [x] 1.2 Style the modal with a border, background, and center alignment
- [x] 1.3 Handle Input submission: fetch/validate URL, add feed to storage, dismiss screen with result
- [x] 1.4 Handle Escape to dismiss the modal without adding
- [x] 1.5 Remove the old `#input-bar` widget and `_input_mode == "add"` logic from `RSSReaderApp`
- [x] 1.6 Update `action_add_feed` to push the `AddFeedScreen` and refresh feed list on dismiss

## 2. Testing

- [x] 2.1 Update TUI tests for add-feed to work with the new modal screen
- [x] 2.2 Verify all existing tests still pass
