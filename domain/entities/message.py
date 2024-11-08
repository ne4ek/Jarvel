from dataclasses import dataclass, field
from datetime import datetime, timedelta
from .user import User
from typing import Optional


@dataclass
class Message:
    message_id: Optional[int] = field(default=None)
    chat_message_id: Optional[str] = field(default=None)
    author_id: Optional[int] = field(default=None)
    company_code: Optional[str] = field(default=None)
    text: Optional[str] = field(default=None)
    date: Optional[datetime] = field(default=None)
    replied_message_id: Optional[int] = field(default=None)

    chat_id: Optional[int] = field(default=None)
    is_bot_message: Optional[bool] = field(default=False)
    author_user: Optional[User] = field(default=None)

