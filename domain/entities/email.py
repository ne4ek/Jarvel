from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Email:
    topic: Optional[str] = field(default=None)
    body: Optional[str] = field(default=None)
    recipients: Optional[list[str]] = field(default=None)
    attachment_paths: Optional[list[str] | str] = field(default=None)
