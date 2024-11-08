from dataclasses import dataclass, field
from typing import Optional

@dataclass
class UnknownUser:
    username: Optional[str] = field(default=None)
    full_name: Optional[str] = field(default=None)
    email: Optional[str] = field(default=None)