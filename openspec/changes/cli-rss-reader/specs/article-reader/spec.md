## ADDED Requirements

### Requirement: Browse articles in a TUI
The system SHALL provide a terminal user interface for browsing articles. The TUI SHALL display a list of articles sorted by publication date (newest first) with feed name, title, and date.

#### Scenario: Launch TUI with articles available
- **WHEN** user launches the reader and articles exist in storage
- **THEN** the system displays a scrollable list of articles with feed name, title, date, and unread indicator

#### Scenario: Launch TUI with no articles
- **WHEN** user launches the reader and no articles exist in storage
- **THEN** the system displays a message indicating no articles are available and suggests fetching feeds

### Requirement: View article detail
The system SHALL allow users to select an article from the list to view its full content (title, author, date, and body/summary) rendered in the terminal.

#### Scenario: Open an article
- **WHEN** user selects an article from the list
- **THEN** the system displays the article's title, author, publication date, and body/summary in a readable format

#### Scenario: Return to article list
- **WHEN** user is viewing an article and presses the back key
- **THEN** the system returns to the article list with the previously selected article still highlighted

### Requirement: Track read/unread status
The system SHALL track which articles have been read. Articles SHALL be marked as read when opened in the detail view. Unread articles SHALL be visually distinguished in the article list.

#### Scenario: Mark article as read
- **WHEN** user opens an article in the detail view
- **THEN** the article is marked as read and the unread indicator is removed in the list

#### Scenario: Unread articles are visually distinct
- **WHEN** the article list is displayed
- **THEN** unread articles SHALL be visually distinguished from read articles (e.g., bold, color, or icon)

### Requirement: Filter articles by feed
The system SHALL allow users to filter the article list to show only articles from a specific feed.

#### Scenario: Filter to a single feed
- **WHEN** user selects a feed filter in the TUI
- **THEN** the article list shows only articles from the selected feed

#### Scenario: Clear feed filter
- **WHEN** user clears the feed filter
- **THEN** the article list shows articles from all feeds
