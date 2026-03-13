## Why

There is no simple, terminal-native way to aggregate and read RSS feeds without leaving the command line. Developers and power users who live in the terminal need a lightweight tool to subscribe to feeds, fetch updates, and read articles — all from the CLI.

## What Changes

- Add a new CLI application that aggregates multiple RSS/Atom feeds
- Support adding, removing, and listing feed subscriptions
- Fetch and parse feed content with configurable refresh intervals
- Display articles in a readable terminal format with TUI browsing
- Persist feed subscriptions and read state locally

## Capabilities

### New Capabilities
- `feed-management`: Subscribe to, unsubscribe from, and list RSS/Atom feed sources. Persistent local storage of feed configuration.
- `feed-fetching`: Fetch and parse RSS 2.0 and Atom feed formats. Handle network errors, timeouts, and malformed feeds gracefully.
- `article-reader`: Display feed articles in a browsable TUI with list navigation, article detail view, and read/unread tracking.
- `cli-interface`: Top-level CLI commands and flags for all operations (add, remove, list, fetch, read). Standard Unix conventions for flags and output.

### Modified Capabilities

_(none — this is a new project)_

## Impact

- New binary/entry point added to the project
- New dependencies: RSS/Atom parsing library, TUI framework, local storage (SQLite or flat file)
- No existing code is affected — this is a greenfield addition
