from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile
)
from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.meeting import Meeting
from domain.entities.user import User
from ics import Calendar, Event
from datetime import datetime, timedelta
from icecream import ic
import pytz
import os


class SendTelegramMeetingNotificationService:
    def __init__(self, bot: Bot, repositories: RepositoriesDependencyProvider):
        self.bot = bot
        self.meeting_repository = repositories.get_meetings_repository()

    async def send_meeting_is_set_to_all(self, meeting: Meeting):
        invitation_type = meeting.invitation_type
        ics_filepath = self.__create_ics_file(meeting)
        
        await self.send_moderator_meeting_is_set(meeting, ics_filepath)
        if invitation_type == "telegram":
            await self.send_telegram_participants_meeting_is_set(meeting, ics_filepath)
        os.remove(ics_filepath)
    
    async def send_moderator_meeting_is_set(self, meeting: Meeting, ics_filepath: str):
        participants_users: dict = meeting.participants_users
        moderator_user = meeting.moderator_user
        invitation_type = meeting.invitation_type
        topic = meeting.topic
        duration = meeting.duration
        link = meeting.link if meeting.link else "не указана"
        
        moderator_text = \
'''
Вы были назначены модератором встречи.
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👥 Известные участники:
{known_participants}
{unknown_participants}
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
'''
        known_participants = ""
        if participants_users.get("known_participants"):
            if invitation_type == "email":
                for participant in participants_users["known_participants"]:
                    known_participants += f"{participant.full_name} ({participant.email})\n"
            else:
                for participant in participants_users["known_participants"]:
                    known_participants += f"{participant.full_name} ({participant.username})\n"
        
        unknown_participants = ""
        if participants_users.get("unknown_participants"):
            unknown_participants = "❓ Неизвестные участники:\n"
            for unknown_user in participants_users.get("unknown_participants"):
                unknown_user_name = ""
                unknown_user_username = ""
                unknown_user_email = ""
                if unknown_user.full_name:
                    unknown_user_name = unknown_user.full_name
        
                if unknown_user.username:
                    unknown_user_username = f" ({unknown_user.username})"
                if unknown_user.email:
                    unknown_user_email = f" ({unknown_user.email})"
                if unknown_user_username or unknown_user_email:
                    unknown_participants += f"{unknown_user_name}{unknown_user_username}{unknown_user_email}\n"
                elif unknown_user_name:
                    unknown_participants += f"{unknown_user_name}\n"
        
        moderator_text = moderator_text.format(
            topic=topic,
            meeting_datetime=meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК"),
            known_participants=known_participants,
            unknown_participants=unknown_participants,
            link=link,
            duration=duration
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"meeting_moderator confirm meeting_id:{meeting.meeting_id}")],])
        #await self.bot.send_message(chat_id=moderator_user.user_id,
        #                            text=moderator_text,
        #                            reply_markup=keyboard)
        await self.bot.send_document(chat_id=moderator_user.user_id,
                                     document=FSInputFile(ics_filepath),
                                     caption=moderator_text,
                                     reply_markup=keyboard)
    
    async def send_telegram_participants_meeting_is_set(self, meeting: Meeting, ics_filepath: str):
        participants_users: dict = meeting.participants_users
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        duration = meeting.duration
        link = meeting.link if meeting.link else "не указана"
        
        participants_telegram_text = \
'''
Вам назначена встреча!
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👤 Модератор: {moderator}
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
'''
        participants_telegram_text = participants_telegram_text.format(
            topic=topic,
            meeting_datetime=meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК"),
            moderator = f"{moderator_user.full_name} ({moderator_user.username})",
            link=link,
            duration=duration
        )
        if participants_users.get("known_participants"):
            for participant in participants_users["known_participants"]:
                if participant.user_id != moderator_user.user_id:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="✅ Подтвердить участие", callback_data=f"meeting_participant confirm meeting_id:{meeting.meeting_id}")],
                            [InlineKeyboardButton(text="❌ Отказаться от участия", callback_data=f"meeting_participant decline meeting_id:{meeting.meeting_id}")]
                        ])
                    try:
                        await self.bot.send_document(chat_id=participant.user_id,
                                                 document=FSInputFile(ics_filepath),
                                                 caption=participants_telegram_text,
                                                 reply_markup=keyboard)
                    except:
                        pass
    
    async def send_email_participants_meeting_is_set(self, meeting: Meeting):
        participants_users: dict = meeting.participants_users
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        duration = meeting.duration
        link = meeting.link if meeting.link else "не указана"
    
    async def send_meeting_reminder_to_moderator(self, meeting_id: int, remind_datetime: datetime):
        meeting: Meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        if meeting.remind_datetime != remind_datetime:
            return
        participants_users: dict = meeting.participants_users
        moderator_user = meeting.moderator_user
        invitation_type = meeting.invitation_type
        topic = meeting.topic
        duration = meeting.duration
        link = meeting.link if meeting.link else "не указана"
        ics_filepath = self.__create_ics_file(meeting)
        moderator_text = \
'''
Напоминание!
Вы были назначены модератором встречи.
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👥 Известные участники:
{known_participants}
{unknown_participants}
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
'''
        known_participants = ""
        if participants_users.get("known_participants"):
            if invitation_type == "email":
                for participant in participants_users["known_participants"]:
                    known_participants += f"{participant.full_name} ({participant.email})\n"
            else:
                for participant in participants_users["known_participants"]:
                    known_participants += f"{participant.full_name} ({participant.username})\n"
        
        unknown_participants = ""
        ic(participants_users.get("unknown_participants"))
        if participants_users.get("unknown_participants"):
            unknown_participants = "❓ Неизвестные участники:\n"
            for unknown_user in participants_users.get("unknown_participants"):
                unknown_user_name = ""
                unknown_user_username = ""
                unknown_user_email = ""
                if unknown_user.full_name:
                    unknown_user_name = unknown_user.full_name
        
                if unknown_user.username:
                    unknown_user_username = f" ({unknown_user.username})"
                if unknown_user.email:
                    unknown_user_email = f" ({unknown_user.email})"
                if unknown_user_username or unknown_user_email:
                    unknown_participants += f"{unknown_user_name}{unknown_user_username}{unknown_user_email}\n"
                elif unknown_user_name:
                    unknown_participants += f"{unknown_user_name}\n"
        
        moderator_text = moderator_text.format(
            topic=topic,
            meeting_datetime=meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК"),
            known_participants=known_participants,
            unknown_participants=unknown_participants,
            link=link,
            duration=duration
        )
        try:
            await self.bot.send_document(chat_id=moderator_user.user_id,
                                     document=FSInputFile(ics_filepath),
                                     caption=moderator_text)
        except:
            pass
    
    async def send_meeting_reminder_to_participants(self, meeting_id: int, remind_datetime: datetime):
        meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        if meeting.remind_datetime != remind_datetime:
            return
        participants_users: dict = meeting.participants_users
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        duration = meeting.duration
        link = meeting.link if meeting.link else "не указана"
        ics_filepath = self.__create_ics_file(meeting)
        
        participants_telegram_text = \
'''
Напоминание!
Ранее вам была назначена встреча!
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👤 Модератор: {moderator}
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
'''
        participants_telegram_text = participants_telegram_text.format(
            topic=topic,
            meeting_datetime=meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК"),
            moderator = f"{moderator_user.full_name} ({moderator_user.username})",
            link=link,
            duration=duration
        )
        if participants_users.get("known_participants"):
            for participant in participants_users["known_participants"]:
                if participant.user_id != moderator_user.user_id:
                    #await self.bot.send_message(chat_id=participant.user_id,
                    #                            text=participants_telegram_text,
                    #                            reply_markup=keyboard)
                    try:
                        await self.bot.send_document(chat_id=participant.user_id,
                                                 document=FSInputFile(ics_filepath),
                                                 caption=participants_telegram_text)
                    except:
                        pass
        os.remove(ics_filepath)
    
    async def send_moderator_user_declined_participation(self, meeting: Meeting, user_declined: User):
        ic(meeting)
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        meeting_datetime = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
        moderator_text = \
'''
Информация по встрече обновлена!
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}

Пользователь {participant_name} ({participant_username}) отказался от участия во встрече.
'''
        moderator_text = moderator_text.format(
            topic=topic,
            meeting_datetime=meeting_datetime,
            participant_name=user_declined.full_name,
            participant_username=user_declined.username
        )
        try:
            await self.bot.send_message(chat_id=moderator_user.user_id,
                                        text=moderator_text)
        except:
            pass
    
    async def send_moderator_changed_meeting_link(self, meeting: Meeting):
        new_link = meeting.link
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        meeting_datetime = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
        ics_file = self.__create_ics_file(meeting)
        participants_text = \
'''
Информация о встрече обновлена!
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}

Модератор {moderator_name} ({moderator_username}) изменил ссылку на встречу!
Новая ссылка на встречу: {new_link}
'''
        participants_text = participants_text.format(topic=topic,
                                                     meeting_datetime=meeting_datetime,
                                                     moderator_name=moderator_user.full_name,
                                                     moderator_username=moderator_user.username,
                                                     new_link=new_link)
        for participant in meeting.participants_users.get("known_participants"):
            if participant.user_id != moderator_user.user_id:
                await self.bot.send_document(chat_id=participant.user_id,
                                             document=FSInputFile(ics_file),
                                             caption=participants_text)
        if os.path.exists(ics_file):
            os.remove(ics_file)
    
    async def send_moderator_changed_meeting_datetime(self, meeting: Meeting):
        new_meeting_datetime = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
        moderator_user = meeting.moderator_user
        topic = meeting.topic
        ics_file = self.__create_ics_file(meeting)
        participants_text = \
'''
Информация о встрече обновлена!
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}

Модератор {moderator_name} ({moderator_username}) изменил время встречи!
'''
        participants_text = participants_text.format(topic=topic,
                                                     meeting_datetime=new_meeting_datetime,
                                                     moderator_name=moderator_user.full_name,
                                                     moderator_username=moderator_user.username)
        for participant in meeting.participants_users.get("known_participants"):
            if participant.user_id != moderator_user.user_id:
                await self.bot.send_document(chat_id=participant.user_id,
                                             document=FSInputFile(ics_file),
                                             caption=participants_text)
        if os.path.exists(ics_file):
            os.remove(ics_file)
    
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