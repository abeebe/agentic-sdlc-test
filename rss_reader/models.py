from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Feed:
    id: Optional[int]
    title: str
    url: str
    link: str
    unread_count: int = 0


@dataclass
class Article:
    id: Optional[int]
    feed_id: int
    guid: str
    title: str
    link: str
    author: Optional[str]
    published: Optional[datetime]
    summary: str
    is_read: bool = False
    is_favorite: bool = False
    feed_title: Optional[str] = None
