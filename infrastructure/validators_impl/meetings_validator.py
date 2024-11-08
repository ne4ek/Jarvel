from datetime import datetime, timedelta

from application.meetings.validators.meetings_validators import MeetingsValidator
from domain.entities.meeting import Meeting


class MeetingsValidatorImpl(MeetingsValidator):
    @staticmethod
    def validate_author(meeting: Meeting = None):
        if meeting.author_user is None:
            raise ValueError("author_user")
        

    @staticmethod
    def validate_moderator(meeting: Meeting = None):
        if meeting.moderator_user is None:
            raise ValueError("moderator_user")
        
    @staticmethod
    def validate_known_participants( meeting: Meeting = None):
        if not meeting.participants_users.get("known_participants"):
            raise ValueError("known_participants")

    @staticmethod
    def validate_company_code(meeting: Meeting = None):
        if meeting.company_code is None:
            raise ValueError("company_code")
        
    @staticmethod
    def validate_topic(meeting: Meeting = None):
        if meeting.topic is None:
            raise ValueError("topic")
        
    @staticmethod
    def validate_link(meeting: Meeting = None):
        if meeting.link is None:
            raise ValueError("link")
        
    @staticmethod
    def validate_duration(meeting: Meeting = None):
        if meeting.duration is None:
            raise ValueError("duration")
        
    
    @staticmethod
    def validate_invitation_type(meeting: Meeting = None):
        if meeting.invitation_type is None:
            raise ValueError("invitation_type")
        
    
    @staticmethod
    def validate_meeting_time(meeting: Meeting = None):
        if meeting.meeting_datetime is None:
            raise ValueError("meeting_time")
        
    
    @staticmethod
    def validate_remind_time(meeting: Meeting = None):
        if meeting.remind_datetime is None:
            raise ValueError("remind_datetime")

    @staticmethod
    def validate_created_meeting(meeting: Meeting):
        try:
            MeetingsValidatorImpl.validate_author(meeting)
            MeetingsValidatorImpl.validate_moderator(meeting)
            MeetingsValidatorImpl.validate_known_participants(meeting)
            MeetingsValidatorImpl.validate_company_code(meeting)
            MeetingsValidatorImpl.validate_topic(meeting)
            #MeetingsValidatorImpl.validate_link(meeting.link)
            MeetingsValidatorImpl.validate_duration(meeting)
            MeetingsValidatorImpl.validate_invitation_type(meeting)
            MeetingsValidatorImpl.validate_meeting_time(meeting)   
            MeetingsValidatorImpl.validate_remind_time(meeting)
            return True
        except Exception as e:
            pass
            return False