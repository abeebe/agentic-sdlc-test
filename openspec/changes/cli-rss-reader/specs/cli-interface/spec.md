## ADDED Requirements

### Requirement: Add command
The system SHALL provide a `rss add <url>` command to subscribe to a feed. An optional `--name` flag SHALL allow the user to set a custom display name for the feed.

#### Scenario: Add feed with default name
- **WHEN** user runs `rss add https://example.com/feed.xml`
- **THEN** the system subscribes to the feed using the feed's own title as the display name

#### Scenario: Add feed with custom name
- **WHEN** user runs `rss add https://example.com/feed.xml --name "My Feed"`
- **THEN** the system subscribes to the feed using "My Feed" as the display name

### Requirement: Remove command
The system SHALL provide a `rss remove <name-or-id>` command to unsubscribe from a feed.

#### Scenario: Remove a feed by name
- **WHEN** user runs `rss remove "My Feed"`
- **THEN** the system removes the matching feed subscription and its articles

### Requirement: List command
The system SHALL provide a `rss list` command to display all subscribed feeds.

#### Scenario: List all feeds
- **WHEN** user runs `rss list`
- **THEN** the system prints a table of feeds with columns: name, URL, unread count

### Requirement: Fetch command
The system SHALL provide a `rss fetch` command to update all feeds. An optional argument SHALL allow fetching a specific feed by name or ID.

#### Scenario: Fetch all feeds
- **WHEN** user runs `rss fetch`
- **THEN** the system fetches all subscribed feeds and reports results

#### Scenario: Fetch a specific feed
- **WHEN** user runs `rss fetch "My Feed"`
- **THEN** the system fetches only the specified feed and reports results

### Requirement: Read command launches TUI
The system SHALL provide a `rss read` command that launches the interactive TUI article reader. An optional feed name argument SHALL pre-filter to that feed.

#### Scenario: Launch TUI for all feeds
- **WHEN** user runs `rss read`
- **THEN** the system launches the TUI showing articles from all feeds

#### Scenario: Launch TUI filtered to a feed
- **WHEN** user runs `rss read "My Feed"`
- **THEN** the system launches the TUI pre-filtered to articles from "My Feed"

### Requirement: Exit codes follow Unix conventions
The system SHALL return exit code 0 on success and non-zero on failure. Errors SHALL be written to stderr.

#### Scenario: Successful command
- **WHEN** any command completes successfully
- **THEN** the process exits with code 0

#### Scenario: Failed command
- **WHEN** a command encounters an error (e.g., invalid URL, network failure)
- **THEN** the process exits with a non-zero code and writes an error message to stderr
