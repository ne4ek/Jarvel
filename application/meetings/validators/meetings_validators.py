from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from domain.entities.meeting import Meeting


class MeetingsValidator(ABC):
    @staticmethod
    @abstractmethod
    def validate_author(author_id: int, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_moderator(moderator_id: int, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_known_participants(known_participants: list[int], meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_company_code(company_code: str, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_topic(topic: str, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_link(link: str, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_duration(duration: str, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_invitation_type(invitation_type: str, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_meeting_time(meeting_time: datetime, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_remind_time(remind_time: datetime, meeting: Meeting = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_created_meeting(meeting: Meeting):
        pass


