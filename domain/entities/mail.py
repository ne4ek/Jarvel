from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
from .user import User
from .unknown_user import UnknownUser
from aiogram import types

@dataclass
class Mail:
    mailing_id: Optional[int] = field(default=None)
    author_id: Optional[int] = field(default=None)
    recipients_ids: Optional[int] = field(default=None)

    author_user: Optional[User] = field(default=None)
    recipients: Optional[Dict[str, Union[UnknownUser, User]]] = field(default=None)

    topic: Optional[str] = field(default=None)
    body: Optional[str] = field(default=None)
    contact_type: Optional[str] = field(default=None)
    attachment: Optional[types.Message| list[types.Message]] = field(default=None)
    send_delay: Optional[datetime] = field(default=None)
    created_at: Optional[datetime] = field(default=None)
    send_at: Optional[datetime] = field(default=None)
    unknown_recipients_data: Optional[List[str]] = field(default=None)
    company_code: Optional[str] = field(default=None)
