## ADDED Requirements

### Requirement: Add a feed subscription
The system SHALL allow users to subscribe to an RSS or Atom feed by providing a URL. The feed URL SHALL be validated by attempting to fetch and parse it before saving. The system SHALL reject duplicate feed URLs.

#### Scenario: Successfully add a new feed
- **WHEN** user provides a valid RSS/Atom feed URL that is not already subscribed
- **THEN** the system fetches the feed, stores the subscription (URL, title, site link), and confirms the addition with the feed title

#### Scenario: Add a duplicate feed
- **WHEN** user provides a feed URL that is already subscribed
- **THEN** the system SHALL display an error indicating the feed is already subscribed

#### Scenario: Add an invalid URL
- **WHEN** user provides a URL that does not resolve to a valid RSS/Atom feed
- **THEN** the system SHALL display an error indicating the URL is not a valid feed

### Requirement: Remove a feed subscription
The system SHALL allow users to unsubscribe from a feed. Removing a feed SHALL also delete all associated articles from local storage.

#### Scenario: Remove an existing feed
- **WHEN** user specifies a subscribed feed (by title or ID)
- **THEN** the system removes the feed and all its articles from storage and confirms the removal

#### Scenario: Remove a non-existent feed
- **WHEN** user specifies a feed that does not exist in subscriptions
- **THEN** the system SHALL display an error indicating the feed was not found

### Requirement: List feed subscriptions
The system SHALL display all subscribed feeds with their title, URL, and the number of unread articles.

#### Scenario: List feeds with subscriptions
- **WHEN** user requests the feed list and subscriptions exist
- **THEN** the system displays each feed's title, URL, and unread article count

#### Scenario: List feeds with no subscriptions
- **WHEN** user requests the feed list and no subscriptions exist
- **THEN** the system displays a message indicating no feeds are subscribed
