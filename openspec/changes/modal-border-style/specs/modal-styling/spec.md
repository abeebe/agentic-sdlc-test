## ADDED Requirements

### Requirement: Modal border matches layout dividers
The add-feed modal dialog border SHALL use the same color as the layout divider borders (`$surface-lighten-2`) instead of the accent color.

#### Scenario: Modal border color is consistent with layout
- **WHEN** user presses `a` to open the add-feed modal
- **THEN** the modal border color matches the dark blue used by the feed list and article list dividers
