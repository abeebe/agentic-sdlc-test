## ADDED Requirements

### Requirement: Favorite an article
The system SHALL allow users to toggle the favorite/star status of an article in the TUI reader. Favorited articles SHALL be visually indicated in the article list with a star icon.

#### Scenario: Favorite an article
- **WHEN** user highlights an article in the article list and presses the favorite key
- **THEN** the article is marked as favorite in storage and a star indicator appears next to it in the list

#### Scenario: Unfavorite an article
- **WHEN** user highlights a favorited article and presses the favorite key
- **THEN** the article's favorite status is removed from storage and the star indicator disappears

### Requirement: Filter to favorites
The system SHALL provide a "Favorites" entry in the feed list pane that, when selected, filters the article list to show only favorited articles across all feeds.

#### Scenario: View only favorites
- **WHEN** user selects the "Favorites" entry in the feed list pane
- **THEN** the article list shows only articles marked as favorite, from all feeds

#### Scenario: No favorites exist
- **WHEN** user selects "Favorites" and no articles are favorited
- **THEN** the article list shows an empty state message

### Requirement: Persist favorite status in storage
The storage layer SHALL support an `is_favorite` flag on articles and provide methods to toggle it and query favorited articles.

#### Scenario: Toggle favorite in storage
- **WHEN** the toggle favorite method is called with an article ID
- **THEN** the article's `is_favorite` flag is flipped (false→true or true→false) and persisted

#### Scenario: Query favorite articles
- **WHEN** favorites are queried from storage
- **THEN** only articles with `is_favorite = true` are returned
