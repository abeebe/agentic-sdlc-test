# RSS Reader

A terminal-based RSS/Atom feed aggregator and reader with a full TUI interface built on [Textual](https://textual.textualize.io/).

## Features

- Subscribe to RSS and Atom feeds
- Three-pane TUI: feed list, article list, article detail
- Favorite/star articles for later
- Delete articles you're done with
- Vim-style navigation (`j`/`k`)
- In-app feed management (add, fetch, remove)
- SQLite storage — your data stays local

## Requirements

- Python 3.10+

## Installation

```bash
# Clone the repo
git clone https://github.com/abeebe/agentic-sdlc-test.git
cd agentic-sdlc-test

# Create a virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/abeebe/agentic-sdlc-test.git
```

## Usage

### CLI Commands

```bash
# Subscribe to a feed
rss add https://example.com/feed.xml

# List subscribed feeds
rss list

# Fetch new articles from all feeds
rss fetch

# Fetch from a specific feed
rss fetch "Feed Name"

# Remove a feed
rss remove "Feed Name"
```

### TUI Reader

```bash
# Launch the reader with all feeds
rss read

# Launch filtered to a specific feed
rss read "Feed Name"
```

### TUI Keybindings

| Key     | Action             |
|---------|--------------------|
| `j`/`k` | Navigate up/down   |
| `Space` | Select article     |
| `Enter` | Select article     |
| `s`     | Toggle favorite    |
| `d`     | Delete article     |
| `a`     | Add feed           |
| `F`     | Fetch all feeds    |
| `r`     | Remove feed        |
| `q`     | Quit               |

## Development

```bash
# Install in editable mode with test dependencies
pip install -e .
pip install pytest pytest-asyncio

# Run tests
pytest
```
