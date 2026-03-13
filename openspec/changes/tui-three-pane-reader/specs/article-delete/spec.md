## ADDED Requirements

### Requirement: Delete an article
The system SHALL allow users to delete an individual article from the TUI reader. Deleting an article SHALL remove it from local storage permanently and remove it from the visible article list immediately.

#### Scenario: Delete an article from the list
- **WHEN** user highlights an article in the article list and presses the delete key
- **THEN** the article is removed from storage and disappears from the article list

#### Scenario: Cursor adjusts after deletion
- **WHEN** user deletes an article that is not the last item in the list
- **THEN** the cursor moves to the next article in the list

#### Scenario: Cursor adjusts when deleting last item
- **WHEN** user deletes the last article in the list
- **THEN** the cursor moves to the previous article, or the list shows an empty state if no articles remain

### Requirement: Delete article from storage
The storage layer SHALL provide a method to delete a single article by its ID.

#### Scenario: Delete existing article
- **WHEN** an article ID is passed to the delete method
- **THEN** the article is removed from the database and no longer appears in query results
