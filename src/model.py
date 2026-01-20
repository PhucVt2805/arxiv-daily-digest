from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from beanie import Document
from pydantic import Field

class ArxivPaper(Document):
    """
    Lưu trữ thông tin bài báo khoa học.
    Collection: arxiv_papers
    """
    id: str = Field(alias="_id")
    title: str
    author: List[str]
    arxiv_url: str
    pdf_url: str
    published_date: datetime
    updated_date: datetime
    summary: str
    prime_category: str
    categories: List[str]
    crawled_at: date = Field(default_factory=lambda: datetime.now(timezone.utc).date())

    class Settings:
        name = "arxiv_papers"

class ChatSession(Document):
    """
    Lưu trữ lịch sử chat của người dùng.
    Collection: chat_sessions
    """
    user_id: str
    paper_id: Optional[str] = None
    messages: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "chat_sessions"