from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Company:
    company_id: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    code: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    owner_id: Optional[int] = field(default=None)
    users_id: Optional[list[int]] = field(default=None)
