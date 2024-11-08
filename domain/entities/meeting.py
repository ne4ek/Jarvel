from dataclasses import dataclass, field
from datetime import datetime, timedelta, time, date
from typing import Optional, List, Dict, Union
from .user import User
from .unknown_user import UnknownUser


@dataclass
class Meeting:
    meeting_id: Optional[int] = field(default=None)
    moderator_id: Optional[int] = field(default=None)
    participants_id: Optional[list] = field(default=None)
    topic: Optional[str] = field(default=None)
    link: Optional[str] = field(default=None)
    meeting_datetime: Optional[datetime] = field(default=None)
    created_at: Optional[datetime] = field(default=None)
    invitation_type: Optional[str] = field(default=None)
    remind_datetime: Optional[datetime] = field(default=None)
    duration: Optional[str] = field(default=None)
    author_id: Optional[int] = field(default=None)
    company_code: Optional[str] = field(default=None)
    unknown_participants_data: Optional[List[str]] = field(default=None)
    status: Optional[str] = field(default=None)
    
    author_user: Optional[User] = field(default=None)
    moderator_user: Optional[User] = field(default=None)
    participants_users: Optional[Dict[str, Union[UnknownUser, User]]] = field(default_factory=lambda: {"known_participants": [], "unknown_participants": []})
    _known_participants_users: Optional[List[User]] = field(default=None)
    
    @property
    def known_participants_users(self) -> List[User]:
        return self._known_participants_users
    
    @known_participants_users.setter
    def known_participants_users(self, users: List[User]):
        self._known_participants_users = users
        self.participants_id = [user.user_id for user in users]
        self.participants_users["known_participants"] = users