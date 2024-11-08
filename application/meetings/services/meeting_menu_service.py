from application.providers.repositories_provider import RepositoriesDependencyProvider
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile
)
from domain.entities.meeting import Meeting
from .telegram_meeting_notification_service import SendTelegramMeetingNotificationService
from .meeting_scheduler_job_service import MeetingJobService
from ics import Calendar, Event
from datetime import datetime, timedelta
from ai.assistants.meeting_assistant.meeting_assistant import MeetingAssistant
import pytz


class MeetingMenuService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider, meeting_assistant: MeetingAssistant, 
                 tg_notification_service: SendTelegramMeetingNotificationService,
                 job_service: MeetingJobService):
        self.meeting_repository = repository_provider.get_meetings_repository()
        self.user_chat_repository = repository_provider.get_user_chats_repository()
        self.companies_repository = repository_provider.get_companies_repository()
        self.users_repository = repository_provider.get_users_repository()
        self.meeting_assistant = meeting_assistant
        self.tg_notification_service = tg_notification_service
        self.job_service = job_service
    
    async def get_company_keyboard(self, user_id: int):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        companies_codes = await self.companies_repository.get_companies_codes_by_user_id(user_id)
        for company_code in companies_codes:
            text = await self.companies_repository.get_name_by_company_code(company_code[0])
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=text,
                                    callback_data=f"user_go_to choose_meet_filt company_code:{company_code[0]}")]
            )
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        return keyboard
    
    def get_meeting_filters_keyboard(self, company_code: str):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Все встречи", callback_data=f"user_go_to meeting_lst company_code:{company_code}")],
            [InlineKeyboardButton(text="Я модератор", callback_data=f"user_go_to meet_mod_lst company_code:{company_code}")],
            [InlineKeyboardButton(text="Я участник", callback_data=f"user_go_to meet_part_lst company_code:{company_code}")],
            [InlineKeyboardButton(text="Архив", callback_data=f"user_go_to meet_archive company_code:{company_code}")],
            [InlineKeyboardButton(text="К выбору компании", callback_data="user_go_to meet_choose_company")]
        ])
        return keyboard
    
    async def get_all_meeting_list(self, user_id: int, company_code: str):
        meetings = await self.meeting_repository.get_by_status_and_company_code_and_user_id("pending", user_id, company_code)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not meetings:
            text = "У вас нет запланированных встреч!"
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filter company_code:{company_code}")])
            return {"text": text, "keyboard": keyboard}
        
        indentation = " " * (len(meetings) - 3)
        
        text = ""
        meeting_summary = \
'''
{n}. {topic}
{indentation}Время встречи: {meeting_time}
{indentation}Модератор: {moderator_name} ({moderator_username})
{indentation}Сссылка: {link}
{indentation}Продолжительность: {duration}
{indentation}Статус: {status}
--------------------------------
'''
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        for n, meeting in enumerate(meetings):
            moderator = await self.users_repository.get_by_id(meeting.moderator_id)
            meeting_datetime_format = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
            meeting_text = meeting_summary.format(
                n=n+1,
                topic=meeting.topic,
                indentation=indentation,
                meeting_time=meeting_datetime_format,
                moderator_name=moderator.full_name,
                moderator_username = moderator.username,
                link=meeting.link if meeting.link else "неизвестно",
                duration=meeting.duration,
                status="ожидает начала"
            )
            text += meeting_text
            
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to meeting_id:{meeting.meeting_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
        return {"text": text, "keyboard": keyboard}
    
    async def get_moderator_meeting_list(self, user_id: int, company_code: str):
        meetings = await self.meeting_repository.get_by_moderator_id_and_company_code(user_id, company_code, "pending")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not meetings:
            text = "У вас нет запланированных встреч!"
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
            return {"text": text, "keyboard": keyboard}
        
        indentation = " " * (len(meetings) - 3)
        
        text = ""
        meeting_summary = \
'''
{n}. {topic}
{indentation}Время встречи: {meeting_time}
{indentation}Сссылка: {link}
{indentation}Продолжительность: {duration}
{indentation}Статус: {status}
--------------------------------
'''
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        for n, meeting in enumerate(meetings):
            meeting_datetime_format = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
            meeting_text = meeting_summary.format(
                n=n+1,
                topic=meeting.topic,
                indentation=indentation,
                meeting_time=meeting_datetime_format,
                link=meeting.link if meeting.link else "неизвестно",
                duration=meeting.duration,
                status="ожидает начала"
            )
            text += meeting_text
            
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to meeting_id:{meeting.meeting_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
        return {"text": text, "keyboard": keyboard}
    
    async def get_participant_meeting_list(self, user_id: int, company_code: str):
        print(user_id, company_code)
        meetings = await self.meeting_repository.get_by_participant_id_and_company_code(user_id, company_code, "pending")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not meetings:
            text = "У вас нет запланированных встреч!"
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
            return {"text": text, "keyboard": keyboard}
        
        indentation = " " * (len(meetings) - 3)
        
        text = ""
        meeting_summary = \
'''
{n}. {topic}
{indentation}Время встречи: {meeting_time}
{indentation}Модератор: {moderator_name} ({moderator_username})
{indentation}Сссылка: {link}
{indentation}Продолжительность: {duration}
{indentation}Статус: {status}
--------------------------------
'''
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        for n, meeting in enumerate(meetings):
            moderator = await self.users_repository.get_by_id(meeting.moderator_id)
            meeting_datetime_format = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
            meeting_text = meeting_summary.format(
                n=n+1,
                topic=meeting.topic,
                indentation=indentation,
                meeting_time=meeting_datetime_format,
                moderator_name=moderator.full_name,
                moderator_username = moderator.username,
                link=meeting.link if meeting.link else "неизвестно",
                duration=meeting.duration,
                status="ожидает начала"
            )
            text += meeting_text
            
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to meeting_id:{meeting.meeting_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
        return {"text": text, "keyboard": keyboard}
    
    async def archive_meeting_list(self, user_id: int, company_code: str):
        meetings = await self.meeting_repository.get_by_status_and_company_code_and_user_id(status="complete", 
                                                                                      user_id=user_id,
                                                                                      company_code=company_code)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not meetings:
            text = "У вас нет архивных встреч!"
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(meetings) - 3)
        
        text = ""
        meeting_summary = \
'''
{n}. {topic}
{indentation}Время встречи: {meeting_time}
{indentation}Модератор: {moderator_name} ({moderator_username})
{indentation}Статус: {status}
--------------------------------
'''
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        for n, meeting in enumerate(meetings):
            moderator = await self.users_repository.get_by_id(meeting.moderator_id)
            meeting_datetime_format = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
            if meeting.status == "complete":
                status = "завершена"
            elif meeting.status == "cancelled":
                status = "отменена"
            meeting_text = meeting_summary.format(
                n=n+1,
                topic=meeting.topic,
                indentation=indentation,
                meeting_time=meeting_datetime_format,
                moderator_name=moderator.full_name,
                moderator_username = moderator.username,
                status=status
            )
            text += meeting_text
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to meeting_id:{meeting.meeting_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К выбору фильтров", callback_data=f"user_go_to choose_meet_filt company_code:{company_code}")])
        return {"text": text, "keyboard": keyboard}
        
    async def get_my_meeting(self, user_id: int, meeting_id: int):
        #Deprecate pls
        meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        meeting_datetime_format = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        if meeting.status == "pending":
            status = "ожидает начала"
        elif meeting.status == "cancelled":
            status = "отменена"
        elif meeting.status == "complete":
            status = "завершена"
        else:
            status = "неизвестно"

        if user_id == meeting.moderator_id:
            text = \
'''
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👥 Известные участники:
{known_participants}
{unknown_participants}
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
🏷️ Статус: {status}
'''
            known_participants = ""
            participants_users = meeting.participants_users
            invitation_type = meeting.invitation_type
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
            text = text.format(
                       topic=meeting.topic,
                       meeting_datetime=meeting_datetime_format,
                       known_participants=known_participants,
                       unknown_participants=unknown_participants,
                       link=meeting.link,
                       duration=meeting.duration,
                       status=status
                    )
            if meeting.status in ["complete", "cancelled"]:
                keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="Переназначить встречу на другое время", callback_data=f"moderator_set_datetime meeting_id: {meeting_id}")],
                                                 [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            else:
                keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="Изменить ссылку", callback_data=f"moderator_set_link meeting_id:{meeting_id}")],
                                                 [InlineKeyboardButton(text="Изменить время встречи", callback_data=f"moderator_set_datetime meeting_id: {meeting_id}")],
                                                 [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        elif user_id in meeting.participants_id:
            text = \
'''
📌 Тема: {topic}
⏰ Время встречи: {meeting_datetime}
👤 Модератор: {moderator_name} ({moderator_username})
🔗 Ссылка: {link}
🕒 Продолжительность встречи: {duration} мин.
🏷️ Статус: {status}
'''
            text = text.format(topic=meeting.topic,
                               meeting_datetime=meeting_datetime_format,
                               moderator_name=meeting.moderator_user.full_name,
                               moderator_username = meeting.moderator_user.username,
                               link=meeting.link if meeting.link else "неизвестно",
                               duration=meeting.duration,
                               status=status)
            if meeting.status in ["complete", "cancelled"]:
                keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="В главное меню", callback_data=f"user_go_to main_menu")]])
            else:
                keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="❌ Отказаться от участия", callback_data=f"meeting_participant decline meeting_id:{meeting.meeting_id}")],
                                                 [InlineKeyboardButton(text="В главное меню", callback_data=f"user_go_to main_menu")]])

        return {"text": text, "keyboard": keyboard, "ics_file": FSInputFile(self.__create_ics_file(meeting))}
    
    def moderator_change_meeting_link(self, text: str, meeting_id: int):
        text += "\n\nВведите ссылку на встречу"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"user_go_to meeting_id:{meeting_id}")]])
        return {"text": text, "keyboard": keyboard}
    
    async def update_meeting_link(self, user_id: int, meeting_id: int, link: str):
        await self.meeting_repository.set_link(meeting_id, link)
        meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        await self.tg_notification_service.send_moderator_changed_meeting_link(meeting)
        return await self.get_my_meeting(meeting_id=meeting_id,
                                   user_id=user_id)
    
    def moderator_change_meeting_datetime(self, text: str, meeting_id: int):
        text += "\n\nВведите время, когда будет проведена встреча"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data=f"user_go_to meeting_id:{meeting_id}")]])
        return {"text": text, "keyboard": keyboard}
    
    async def update_meeting_datetime(self, user_id: int, text: str, meeting_id: int):
        meeting: Meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        prompt = ""
        current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        meeting_datetime = meeting.meeting_datetime
        remind_datetime = meeting.remind_datetime
        time_diff = meeting_datetime - remind_datetime
        prompt += f"meeting_date: {meeting_datetime.strftime('%d.%m.%Y')}\n"
        prompt += f"meeting_time: {meeting_datetime.strftime('%H:%M')}"
        messages = [
           {"role": "system", "content": prompt},
           {"role": "system", "content": f"Дата на сегодня: {current_datetime.date()}\nВремя сейчас: {current_datetime.time()}"},
           {"role": "user", "content": text}
        ]
        new_meeting_datetime = await self.meeting_assistant.change_meeting_datetime(messages, meeting.company_code)
        if new_meeting_datetime is not None:
            meeting.meeting_datetime = new_meeting_datetime
            meeting.remind_datetime = new_meeting_datetime - time_diff
        await self.meeting_repository.set_meeting_datetime(meeting)
        if meeting.invitation_type == "telegram" and meeting.status == "pending":
            await self.tg_notification_service.send_moderator_changed_meeting_datetime(meeting)
        elif meeting.invitation_type == "telegram" and meeting.status in ["complete", "cancelled"]:
            await self.meeting_repository.set_status(meeting.meeting_id, "pending")
            await self.tg_notification_service.send_meeting_is_set_to_all(meeting)
        await self.meeting_repository.set_meeting_datetime(meeting)
        self.job_service.add_saved_meetings_jobs(meeting)
        return await self.get_my_meeting(meeting_id=meeting_id,
                                   user_id=user_id)
    
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