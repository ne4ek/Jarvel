from .user import User

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from icecream import ic

@dataclass
class Task: 
    """Represents a task entity."""
    task_id: Optional[int] = field(default=None)
    """Unique identifier of the task."""
    
    author_id: Optional[int] = field(default=None)
    """Unique identifier of the task author."""
    
    executor_id: Optional[int] = field(default=None)
    """Unique identifier of the task executor."""

    task: Optional[str] = field(default=None)
    """The full description of the task."""

    deadline_datetime: Optional[datetime] = field(default=None)
    """The deadline of the task."""
    
    task_summary: Optional[str] = field(default=None)
    """The summary of the task."""

    status: Optional[str] = field(default=None)
    """The status of the task."""
    
    tag: Optional[str] = field(default=None)
    """The tag associated with the task."""
    
    created_at: Optional[datetime] = field(default=None)
    """timestamp of when the task had been saved"""
    
    company_code: Optional[str] = field(default=None)
    """The company code associated with the task"""
    
    _executor_user: Optional[User] = field(default=None, repr=False)
    """Task executor as a User object"""
    
    _author_user: Optional[User] = field(default=None, repr=False)
    """Task author as a User object"""
    
    @property
    def executor_user(self) -> Optional[User]:
        return self._executor_user
    
    @executor_user.setter
    def executor_user(self, user: User):
        self._executor_user = user
        if user is not None:
            self.executor_id = user.user_id
        else:
            self.executor_id = None
    
    @property
    def author_user(self) -> Optional[User]:
        return self._author_user
    
    @author_user.setter
    def author_user(self, user: User):
        self._author_user = user
        if user is not None:
            self.author_id = user.user_id
        else:
            self.author_id = None