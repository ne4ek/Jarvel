from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class UserChat:
    user_id: Optional[int] = field(default=None)
    role: Optional[str] = field(default=None)
    company_code: Optional[str] = field(default=None)
