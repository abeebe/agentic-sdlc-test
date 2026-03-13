## ADDED Requirements

### Requirement: Fetch all subscribed feeds
The system SHALL fetch the latest content from all subscribed feeds and store new articles locally. Articles SHALL be identified by their unique ID (guid/id) to avoid duplicates.

#### Scenario: Fetch feeds with new articles
- **WHEN** user triggers a fetch and subscribed feeds contain new articles
- **THEN** the system downloads and stores new articles, displaying a summary of new articles per feed

#### Scenario: Fetch feeds with no new articles
- **WHEN** user triggers a fetch and no new articles are found
- **THEN** the system reports that all feeds are up to date

### Requirement: Fetch a single feed
The system SHALL allow users to fetch updates from a specific feed by title or ID, rather than fetching all feeds.

#### Scenario: Fetch a specific feed
- **WHEN** user specifies a feed to fetch by title or ID
- **THEN** the system fetches only that feed and reports new articles

#### Scenario: Fetch a non-existent feed
- **WHEN** user specifies a feed that does not exist
- **THEN** the system SHALL display an error indicating the feed was not found

### Requirement: Handle feed fetch errors gracefully
The system SHALL handle network errors, timeouts, and malformed feed content without crashing. Errors on one feed SHALL NOT prevent fetching of other feeds.

#### Scenario: Feed URL is unreachable
- **WHEN** a feed URL returns a network error or timeout during fetch
- **THEN** the system logs a warning for that feed and continues fetching remaining feeds

#### Scenario: Feed returns malformed content
- **WHEN** a feed URL returns content that cannot be parsed as RSS or Atom
- **THEN** the system logs a warning for that feed and continues fetching remaining feeds

### Requirement: Support RSS 2.0 and Atom formats
The system SHALL parse both RSS 2.0 and Atom feed formats. For each article, the system SHALL extract: title, link, published date, and summary/content.

#### Scenario: Parse an RSS 2.0 feed
- **WHEN** a feed is in RSS 2.0 format
- **THEN** the system correctly extracts article title, link, publication date, and description

#### Scenario: Parse an Atom feed
- **WHEN** a feed is in Atom format
- **THEN** the system correctly extracts article title, link, updated date, and summary/content
