import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from rss_reader.models import Article, Feed

DEFAULT_DB_PATH = Path.home() / ".rss_reader" / "feeds.db"


class Storage:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        self._migrate()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                link TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER NOT NULL,
                guid TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                link TEXT NOT NULL DEFAULT '',
                author TEXT,
                published TEXT,
                summary TEXT NOT NULL DEFAULT '',
                is_read INTEGER NOT NULL DEFAULT 0,
                is_favorite INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE,
                UNIQUE(feed_id, guid)
            );
        """)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.commit()

    def _migrate(self):
        """Add is_favorite column if missing (migration for existing DBs)."""
        cursor = self.conn.execute("PRAGMA table_info(articles)")
        columns = {row["name"] for row in cursor.fetchall()}
        if "is_favorite" not in columns:
            self.conn.execute(
                "ALTER TABLE articles ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0"
            )
            self.conn.commit()

    def add_feed(self, title: str, url: str, link: str = "") -> Feed:
        cursor = self.conn.execute(
            "INSERT INTO feeds (title, url, link) VALUES (?, ?, ?)",
            (title, url, link),
        )
        self.conn.commit()
        return Feed(id=cursor.lastrowid, title=title, url=url, link=link)

    def remove_feed(self, identifier: str) -> bool:
        # Try by title first, then by ID
        row = self.conn.execute(
            "SELECT id FROM feeds WHERE title = ?", (identifier,)
        ).fetchone()
        if not row:
            try:
                feed_id = int(identifier)
                row = self.conn.execute(
                    "SELECT id FROM feeds WHERE id = ?", (feed_id,)
                ).fetchone()
            except ValueError:
                pass
        if not row:
            return False
        feed_id = row["id"]
        self.conn.execute("DELETE FROM articles WHERE feed_id = ?", (feed_id,))
        self.conn.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
        self.conn.commit()
        return True

    def list_feeds(self) -> list[Feed]:
        rows = self.conn.execute("""
            SELECT f.id, f.title, f.url, f.link,
                   COALESCE(SUM(CASE WHEN a.is_read = 0 THEN 1 ELSE 0 END), 0) as unread_count
            FROM feeds f
            LEFT JOIN articles a ON f.id = a.feed_id
            GROUP BY f.id
            ORDER BY f.title
        """).fetchall()
        return [
            Feed(
                id=r["id"],
                title=r["title"],
                url=r["url"],
                link=r["link"],
                unread_count=r["unread_count"],
            )
            for r in rows
        ]

    def get_feed_by_name(self, name: str) -> Optional[Feed]:
        row = self.conn.execute(
            "SELECT id, title, url, link FROM feeds WHERE title = ?", (name,)
        ).fetchone()
        if not row:
            try:
                feed_id = int(name)
                row = self.conn.execute(
                    "SELECT id, title, url, link FROM feeds WHERE id = ?", (feed_id,)
                ).fetchone()
            except ValueError:
                pass
        if not row:
            return None
        return Feed(id=row["id"], title=row["title"], url=row["url"], link=row["link"])

    def feed_url_exists(self, url: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM feeds WHERE url = ?", (url,)
        ).fetchone()
        return row is not None

    def add_article(self, article: Article) -> bool:
        """Add an article. Returns True if inserted, False if duplicate."""
        try:
            self.conn.execute(
                """INSERT INTO articles (feed_id, guid, title, link, author, published, summary, is_read, is_favorite)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    article.feed_id,
                    article.guid,
                    article.title,
                    article.link,
                    article.author,
                    article.published.isoformat() if article.published else None,
                    article.summary,
                    int(article.is_read),
                    int(article.is_favorite),
                ),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_articles(
        self,
        feed_id: Optional[int] = None,
        unread_only: bool = False,
        favorites_only: bool = False,
    ) -> list[Article]:
        query = """
            SELECT a.id, a.feed_id, a.guid, a.title, a.link, a.author,
                   a.published, a.summary, a.is_read, a.is_favorite, f.title as feed_title
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            WHERE 1=1
        """
        params: list = []
        if feed_id is not None:
            query += " AND a.feed_id = ?"
            params.append(feed_id)
        if unread_only:
            query += " AND a.is_read = 0"
        if favorites_only:
            query += " AND a.is_favorite = 1"
        query += " ORDER BY a.published DESC NULLS LAST"
        rows = self.conn.execute(query, params).fetchall()
        return [
            Article(
                id=r["id"],
                feed_id=r["feed_id"],
                guid=r["guid"],
                title=r["title"],
                link=r["link"],
                author=r["author"],
                published=datetime.fromisoformat(r["published"])
                if r["published"]
                else None,
                summary=r["summary"],
                is_read=bool(r["is_read"]),
                is_favorite=bool(r["is_favorite"]),
                feed_title=r["feed_title"],
            )
            for r in rows
        ]

    def mark_read(self, article_id: int):
        self.conn.execute(
            "UPDATE articles SET is_read = 1 WHERE id = ?", (article_id,)
        )
        self.conn.commit()

    def delete_article(self, article_id: int):
        self.conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
        self.conn.commit()

    def toggle_favorite(self, article_id: int):
        self.conn.execute(
            "UPDATE articles SET is_favorite = CASE WHEN is_favorite = 0 THEN 1 ELSE 0 END WHERE id = ?",
            (article_id,),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
