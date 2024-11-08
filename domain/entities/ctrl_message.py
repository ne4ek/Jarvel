from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
@dataclass
class CtrlMessage:
    job_id: Optional[int] = field(default=None)
    run_date: Optional[datetime] = field(default=None)
    chat_id: Optional[int] = field(default=None)
    ctrl_usernames: Optional[str] = field(default=None)
    reply_message_id: Optional[int] = field(default=None)
    created_at: Optional[datetime] = field(default=None)
    fyi_usernames: Optional[str] = field(default=None)