## MODIFIED Requirements

### Requirement: Browse articles in a TUI
The system SHALL provide a terminal user interface with a three-pane layout: a feed list pane (left), an article list pane (center), and an article detail pane (right). The article list SHALL display articles sorted by publication date (newest first) with feed name, title, and date. The feed list pane SHALL display all subscribed feeds with an "All Feeds" entry at the top.

#### Scenario: Launch TUI with articles available
- **WHEN** user launches the reader and articles exist in storage
- **THEN** the system displays a three-pane layout with feeds on the left, a scrollable article list in the center with feed name, title, date, and unread indicator, and an article detail pane on the right

#### Scenario: Launch TUI with no articles
- **WHEN** user launches the reader and no articles exist in storage
- **THEN** the system displays the three-pane layout with an empty article list showing a message indicating no articles are available

### Requirement: View article detail
The system SHALL allow users to select an article from the center pane to view its full content (title, author, date, and body/summary) in the right detail pane.

#### Scenario: Open an article
- **WHEN** user selects an article in the article list pane
- **THEN** the article's title, author, publication date, and body/summary are displayed in the right detail pane

#### Scenario: Return to article list
- **WHEN** user is viewing an article and navigates back to the article list
- **THEN** the article list retains the cursor/highlight on the previously selected article

### Requirement: Filter articles by feed
The system SHALL allow users to filter the article list by selecting a feed in the left feed list pane.

#### Scenario: Filter to a single feed
- **WHEN** user selects a feed in the feed list pane
- **THEN** the article list pane shows only articles from the selected feed

#### Scenario: Show all feeds
- **WHEN** user selects the "All Feeds" entry in the feed list pane
- **THEN** the article list pane shows articles from all subscribed feeds

### Requirement: Track read/unread status
The system SHALL track which articles have been read. Articles SHALL be marked as read when opened in the detail view. Unread articles SHALL be visually distinguished in the article list.

#### Scenario: Mark article as read
- **WHEN** user opens an article in the detail view
- **THEN** the article is marked as read and the unread indicator is removed in the list

#### Scenario: Unread articles are visually distinct
- **WHEN** the article list is displayed
- **THEN** unread articles SHALL be visually distinguished from read articles (e.g., bold, color, or icon)

## REMOVED Requirements

### Requirement: Filter articles by feed
**Reason**: The keybinding-based feed filter cycling (f/a keys) is replaced by direct feed selection in the left pane of the three-pane layout.
**Migration**: Use the feed list pane on the left to select a feed. Select "All Feeds" to clear the filter.
