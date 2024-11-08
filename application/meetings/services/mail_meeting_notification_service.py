from aiogram import Bot
from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.meeting import Meeting
from ics import Calendar, Event
from datetime import datetime, timedelta
from email.message import EmailMessage
from aiosmtplib import SMTP
import mimetypes
import pytz
import os
from icecream import ic


class SendEmailMeetingNotificationService:
    def __init__(self, repositories: RepositoriesDependencyProvider, bot: Bot):
        self.meeting_repository = repositories.get_meetings_repository()
        self.bot = bot
        self.username = os.getenv("EMAIL")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.hostname = "smtp.gmail.com"
        self.port = 587
    
    async def send_mail_participants_meeting_is_set(self, meeting: Meeting):
        ics_filepath = self.__create_ics_file(meeting)
        participants_users = meeting.participants_users
        known_participants_users = participants_users.get("known_participants")
        known_participants_emails = [user.email for user in known_participants_users]
        unknown_participants_users = participants_users.get("unknown_participants")
        unknown_participants_emails = []
        for unknown_participant in unknown_participants_users:
            if unknown_participant.email:
                unknown_participants_emails.append(unknown_participant.email)
        all_participants_emails = known_participants_emails + unknown_participants_emails
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        body = \
'''
Вам назначена встреча!
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👤 Модератор: {moderator}
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
'''

        body = body.format(topic=topic,
                          meeting_datetime=meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК"),
                          moderator=f"{moderator_user.full_name} ({moderator_user.email})",
                          link=meeting.link,
                          duration=meeting.duration)
        ctype, encoding = mimetypes.guess_type(ics_filepath)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        ic(all_participants_emails)
        async with SMTP(hostname=self.hostname, port=self.port, username=self.username,
                                password=self.password, start_tls=True) as smtp_client:
            for email in all_participants_emails:
                message = EmailMessage()
                message["From"] = self.username
                message["Subject"] = topic
                message.set_content(body)
                message["To"] = email
                with open(ics_filepath, "rb") as ics_file:
                    message.add_attachment(ics_file.read(),
                                           maintype=maintype,
                                           subtype=subtype,
                                           filename="ics_file")
                ic(message["To"], message["From"])
                await smtp_client.send_message(message)
        os.remove(ics_filepath)
            
    def __create_ics_file(self, meeting: Meeting) -> str:
        calendar = Calendar()
    
        topic = meeting.topic
        meeting_datetime = meeting.meeting_datetime
        duration = meeting.duration
        meeting_id = meeting.meeting_id
        link = meeting.link
        moderator_email = meeting.moderator_user.email
        # Создаем событие
        e = Event()
        e.name = topic
        e.begin = meeting_datetime
        e.end = meeting_datetime + timedelta(minutes=float(duration))
        e.uid = f"jarvel_meeting_{meeting_id}"
        e.created = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        if link:
            e.url = link
        e.organizer = moderator_email
        # Добавляем событие в календарь
        calendar.events.add(e)
        with open(f'storage/calendar_files/meeting_reminder_{meeting_id}.ics', 'w', encoding='utf-8') as f:
            f.writelines(calendar.serialize())
        return f'storage/calendar_files/meeting_reminder_{meeting_id}.ics'