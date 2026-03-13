## ADDED Requirements

### Requirement: Add feed from within TUI
The system SHALL allow users to add a new feed subscription from within the TUI by pressing `a`. An input bar SHALL appear prompting for a feed URL. Upon submission, the system SHALL fetch and validate the feed, add it to storage, and refresh the feed list.

#### Scenario: Add a valid feed
- **WHEN** user presses `a`, enters a valid feed URL, and submits
- **THEN** the feed is added to storage, the feed list refreshes to include the new feed, and a confirmation is shown

#### Scenario: Add an invalid feed
- **WHEN** user presses `a`, enters an invalid URL, and submits
- **THEN** an error message is displayed and no feed is added

#### Scenario: Cancel adding a feed
- **WHEN** user presses `a` and then presses Escape before submitting
- **THEN** the input bar closes and no feed is added

### Requirement: Fetch feeds from within TUI
The system SHALL allow users to fetch/update all subscribed feeds from within the TUI by pressing `F` (Shift+f). After fetching, the article list SHALL refresh to show new articles.

#### Scenario: Fetch all feeds
- **WHEN** user presses `F` in the TUI
- **THEN** all subscribed feeds are fetched, new articles are stored, and the article list refreshes with a summary notification

#### Scenario: Fetch with no feeds subscribed
- **WHEN** user presses `F` and no feeds are subscribed
- **THEN** the system displays a message indicating no feeds to fetch

### Requirement: Remove feed from within TUI
The system SHALL allow users to remove a feed subscription from within the TUI by pressing `r` while a feed is highlighted in the feed list. A confirmation prompt SHALL be shown before removal.

#### Scenario: Remove a feed with confirmation
- **WHEN** user highlights a feed in the feed list, presses `r`, and confirms removal
- **THEN** the feed and all its articles are removed from storage, and the feed list and article list refresh

#### Scenario: Cancel feed removal
- **WHEN** user highlights a feed in the feed list, presses `r`, and cancels
- **THEN** no feed is removed and the TUI returns to normal state

#### Scenario: Remove on non-feed entry
- **WHEN** user presses `r` while "All Feeds" or "Favorites" is highlighted
- **THEN** no action is taken
