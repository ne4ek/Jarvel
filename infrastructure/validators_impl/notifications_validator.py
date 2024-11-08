from application.notification.validators.notifications_validator import NotificationsValidator
from datetime import datetime, timedelta


class NotificationsValidatorImpl(NotificationsValidator):
    @staticmethod
    def validate_author_id(author_id: str):
        if author_id is None:
            raise ValueError

    @staticmethod
    def validate_recipients_ids(recipients_ids: str | list[str]):
        if recipients_ids is None:
            raise ValueError

    @staticmethod
    def validate_topic(topic: str):
        if topic is None:
            raise ValueError

    @staticmethod
    def validate_body(body: str):
        if body is None:
            raise ValueError

    @staticmethod
    def validate_destination_platform(destination_platform: str):
        if destination_platform is None:
            raise ValueError

    @staticmethod
    def validate_attachment_paths(attachment_paths: str):
        if attachment_paths is None:
            raise ValueError

    @staticmethod
    def validate_send_delay(send_delay: str):
        if send_delay is None:
            raise ValueError


