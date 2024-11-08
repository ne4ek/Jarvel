from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime 

@dataclass
class GroupChat:
    chat_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    company_code: Optional[str] = field(default=None)
    owner_id: Optional[int] = field(default=None)
    created_at: Optional[datetime] = field(default=None)
