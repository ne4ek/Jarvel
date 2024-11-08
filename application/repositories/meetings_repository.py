from abc import ABC, abstractmethod
from datetime import datetime
from typing import List
from domain.entities.meeting import Meeting


class MeetingsRepository(ABC):
    """
    Meeting repository abstract class.
    """

    @abstractmethod
    def save(self, meeting: Meeting):
        pass

    @abstractmethod
    def get_all(self) -> List[Meeting]:
        pass

    @abstractmethod
    def get_all_meeting_ids(self) -> List[int]:
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: int) -> List[Meeting]:
        pass

    @abstractmethod
    def get_last_n_by_user_id(self, user_id: int, n: int) -> List[Meeting]:
        pass

    @abstractmethod
    def get_by_user_id_filter_deadline(self, user_id: int, deadline: datetime) -> List[Meeting]:
        pass

    @abstractmethod
    def get_by_meeting_id(self, meeting_id: int) -> Meeting:
        pass

    @abstractmethod
    def get_by_moderator_id_and_company_code(self, moderator_id: int, company_code: str, status: str = None) -> List[Meeting]:
        pass
    
    @abstractmethod
    def get_by_participant_id_and_company_code(self, participant_id: int, company_code: str, status: str = None) -> List[Meeting]:
        pass
    
    @abstractmethod
    def get_by_user_id_and_company_code(self, user_id: int, company_code: str) -> List[Meeting]:
        pass
    
    @abstractmethod
    def set_link(self, meeting_id: int, link: str):
        pass
    
    @abstractmethod
    def set_participants(self, participants_ids: List[int], meeting_id: int):
        pass
    
    @abstractmethod
    def set_meeting_datetime(self, meeting: Meeting) -> None:
        pass
    
    @abstractmethod
    def get_by_status_and_company_code_and_user_id(status: str, user_id: int, company_code: str) -> None:
        pass
    
    @abstractmethod
    def set_status(self, meeting_id: int, status: str) -> None:
        pass