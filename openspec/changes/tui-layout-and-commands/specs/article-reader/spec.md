## MODIFIED Requirements

### Requirement: Browse articles in a TUI
The system SHALL provide a terminal user interface with a two-column layout: a feed list pane (left, ~20% width) and a right pane split horizontally into an article list (top, ~40% height) and an article detail view (bottom, ~60% height). The article list SHALL display articles sorted by publication date (newest first) with feed name, title, and date. The feed list pane SHALL display all subscribed feeds with an "All Feeds" entry and a "Favorites" entry at the top.

#### Scenario: Launch TUI with articles available
- **WHEN** user launches the reader and articles exist in storage
- **THEN** the system displays the feed list on the left, article list on the top-right, and article detail on the bottom-right

#### Scenario: Launch TUI with no articles
- **WHEN** user launches the reader and no articles exist in storage
- **THEN** the system displays the layout with an empty article list showing a message indicating no articles are available

### Requirement: View article detail
The system SHALL allow users to select an article from the article list using the Spacebar key. Selecting an article SHALL display its full content (title, author, date, and body/summary) in the bottom detail pane.

#### Scenario: Select an article with spacebar
- **WHEN** user highlights an article in the article list and presses Spacebar
- **THEN** the article's title, author, publication date, and body/summary are displayed in the bottom detail pane

#### Scenario: Return to article list
- **WHEN** user is viewing an article and navigates back to the article list
- **THEN** the article list retains the cursor/highlight on the previously selected article

## ADDED Requirements

### Requirement: Vim-style navigation
The system SHALL support vim-style navigation keys in addition to arrow keys. `j` SHALL move the cursor down and `k` SHALL move the cursor up in the article list and feed list.

#### Scenario: Navigate down with j
- **WHEN** user presses `j` while the article list or feed list is focused
- **THEN** the cursor moves down one row

#### Scenario: Navigate up with k
- **WHEN** user presses `k` while the article list or feed list is focused
- **THEN** the cursor moves up one row
