## MODIFIED Requirements

### Requirement: Add feed from within TUI
The system SHALL allow users to add a new feed subscription from within the TUI by pressing `a`. A centered modal popover SHALL appear with a text input for the feed URL. Upon submission, the system SHALL fetch and validate the feed, add it to storage, and refresh the feed list. The modal SHALL be dismissed on submit or Escape.

#### Scenario: Add a valid feed
- **WHEN** user presses `a`, a centered modal appears, user enters a valid feed URL, and submits
- **THEN** the feed is added to storage, the feed list refreshes, a confirmation is shown, and the modal closes

#### Scenario: Add an invalid feed
- **WHEN** user presses `a`, enters an invalid URL in the modal, and submits
- **THEN** an error message is displayed and no feed is added

#### Scenario: Cancel adding a feed
- **WHEN** user presses `a` and then presses Escape in the modal
- **THEN** the modal closes and no feed is added
