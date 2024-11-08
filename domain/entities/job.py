from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from typing import Optional, Callable


@dataclass
class Job:
    func: Callable = field(default=None)
    trigger: str = field(default=None)
    run_date: datetime = field(default=None)
    args: list = field(default=None)
    job_id: Optional[str] = field(default=None)
    job_type: Optional[str] = field(default=None)