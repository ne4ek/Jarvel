from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta

@dataclass
class UpMessage:
    up_message_id: Optional[int] = field(default=None)
    start_date: Optional[datetime] = field(default=None)
    present_date: Optional[datetime] = field(default=None)
    next_up_date: Optional[datetime] = field(default=None)
    interval: Optional[timedelta] = field(default=None)
    starting_interval: Optional[timedelta] = field(default=None)
    chat_id: Optional[int] = field(default=None)
    up_username: Optional[str] = field(default=None)
    reply_message_id: Optional[int] = field(default=None)
    bot_message_id: Optional[int] = field(default=None)
    fyi_username: Optional[str] = field(default=None)
    is_active: Optional[bool] = field(default=True)