from application.providers.repositories_provider import RepositoriesDependencyProvider
from application.providers.usecases_provider import UseCasesProvider
from application.meetings.services.meeting_scheduler_job_service import MeetingJobService
from .telegram_meeting_notification_service import SendTelegramMeetingNotificationService
from .mail_meeting_notification_service import SendEmailMeetingNotificationService
from domain.contracts.assistant import Assistant
from domain.entities.transcribed_message import TranscribedMessage
from domain.entities.meeting import Meeting
from domain.entities.unknown_user import UnknownUser
from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import Union
from icecream import ic
from datetime import datetime, timedelta
import json
import pytz

class TelegramComposeMeetingService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider, 
                 telegram_meeting_notification_service: SendTelegramMeetingNotificationService,
                 email_meeting_notificaiton_service: SendEmailMeetingNotificationService,
                 meeting_assistant: Assistant, meeting_job_service: MeetingJobService):
        self.telegram_meeting_notification_service = telegram_meeting_notification_service
        self.email_meeting_notification_service = email_meeting_notificaiton_service
        self.company_repository = repository_provider.get_companies_repository()
        self.user_repository = repository_provider.get_users_repository()
        self.meeting_repository = repository_provider.get_meetings_repository()
        self.meeting_assistant = meeting_assistant
        self.meeting_job_service = meeting_job_service
    
    async def change_meeting_topic(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):  
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        bot_message = data.get("meeting").get("message")
        meeting_topic = meeting.topic
        
        messages = [
           {"role": "system", "content": f"topic: {meeting_topic}"},
           {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_meeting_topic = await self.meeting_assistant.change_meeting_topic(messages, company_code)
        meeting.topic = new_meeting_topic
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)

    async def change_meeting_duration(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        bot_message = data.get("meeting").get("message")
        meeting_duration = meeting.duration
        meeting_datetime = meeting.meeting_datetime
        if meeting_datetime:
            messages = [
            {"role": "system", "content": f"meeting_time: {meeting_datetime.strftime('%H:%M')}\nmeeting_duration: {meeting_duration}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
            ]
        else:
            messages = [
            {"role": "system", "content": f"meeting_duration: {meeting_duration}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
            ]
        company_code = await self.__get_company_code(message.chat.id)
        new_meeting_duration = await self.meeting_assistant.change_meeting_duration(messages, company_code)
        meeting.duration = new_meeting_duration
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)

    async def change_meeting_remind_time(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        bot_message = data.get("meeting").get("message")
        meeting_remind_datetime = meeting.remind_datetime
        meeting_datetime = meeting.meeting_datetime
        prompt = ""
        if meeting_datetime:
            prompt += f"meeting_date: {meeting_datetime.strftime('%d.%m.%Y')}\n"
            prompt += f"meeting_time: {meeting_datetime.strftime('%H:%M')}\n"
        else:
            prompt += f"meeting_date: None\nmeeting_time: None"
        if meeting_remind_datetime:
            prompt += f"remind_date: {meeting_remind_datetime.strftime('%d.%m.%Y')}\n"
            prompt += f"remind_time: {meeting_remind_datetime.strftime('%H:%M')}"
        else:
            prompt += f"remind_date: None\n remind_time: None"
        messages = [
           {"role": "system", "content": prompt},
           {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_meeting_remind_datetime = await self.meeting_assistant.change_meeting_remind_time(messages, company_code, meeting_datetime)
        meeting.remind_datetime = new_meeting_remind_datetime
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)
    
    async def change_meeting_participants(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        bot_message = data.get("meeting").get("message")
        if meeting.participants_users:
            known_participants_names = [participant.full_name for participant in meeting.participants_users.get("known_participants")]
            unknown_participants_names = []
            for unknown_user in meeting.participants_users.get("unknown_participants"):
                user = ""
                if unknown_user.full_name:
                    user += unknown_user.full_name
                if unknown_user.email:
                    user += f"({unknown_user.email})"
                if unknown_user.username:
                    user += f"({unknown_user.username})"
                unknown_participants_names.append(user)
        else:
            known_participants_names = []
            unknown_participants_names = []
        all_participant_names = known_participants_names + unknown_participants_names
        messages = [
           {"role": "system", "content": f"participants_names: {all_participant_names}"},
           {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_meeting_participants: dict = await self.meeting_assistant.change_meeting_participants(messages, company_code)
        meeting.participants_users = new_meeting_participants
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)
    
    async def change_meeting_moderator(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        bot_message = data.get("meeting").get("message")
        moderator_user = meeting.moderator_user
        if moderator_user:
            moderator_name = moderator_user.full_name
        else:
            moderator_name = "None"
        messages = [
           {"role": "system", "content": f"moderator: {moderator_name}"},
           {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_meeting_moderator = await self.meeting_assistant.change_meeting_moderator(messages, company_code)
        meeting.moderator_user = new_meeting_moderator
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)
    
    async def change_meeting_datetime(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        bot_message = data.get("meeting").get("message")
        meeting_datetime = meeting.meeting_datetime
        prompt = ""
        if meeting_datetime:
            prompt += f"meeting_date: {meeting_datetime.strftime('%d.%m.%Y')}\n"
            prompt += f"meeting_time: {meeting_datetime.strftime('%H:%M')}\n"
        else:
            prompt += f"meeting_date: None\nmeeting_time: None"
        current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        messages = [
           {"role": "system", "content": prompt},
           {"role": "system", "content": f"Дата на сегодня: {current_datetime.date()}\nВремя сейчас: {current_datetime.time()}"},
           {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_meeting_datetime = await self.meeting_assistant.change_meeting_datetime(messages, company_code)
        remind_datetime = meeting.remind_datetime
        meeting_datetime = meeting.meeting_datetime
        
        if not meeting.remind_datetime and new_meeting_datetime:
            meeting.remind_datetime = new_meeting_datetime - timedelta(minutes=5)
        elif meeting_datetime and remind_datetime:
            time_diff = new_meeting_datetime - meeting_datetime
            meeting.remind_datetime = remind_datetime + time_diff
        meeting.meeting_datetime = new_meeting_datetime
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)
    
    async def change_meeting_link(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        meeting.link = message.text
        bot_message = data.get("meeting").get("message")
        await state.update_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting)

    async def save_meeting(self, state: FSMContext):
        data = await state.get_data()
        meeting: Meeting = data.get("meeting").get("entity")
        meeting.author_id = meeting.author_user.user_id
        meeting.moderator_id = meeting.moderator_user.user_id
        meeting.participants_id = [user.user_id for user in meeting.participants_users.get("known_participants")]
        meeting.unknown_participants_data = [self.__unknown_user_to_json(unknown_user) for unknown_user in meeting.participants_users.get("unknown_participants")]
        meeting_id = await self.meeting_repository.save(meeting)
        meeting.meeting_id = meeting_id
        meeting.status = "pending"
        await self.telegram_meeting_notification_service.send_meeting_is_set_to_all(meeting)
        if meeting.invitation_type == "email":
            await self.email_meeting_notification_service.send_mail_participants_meeting_is_set(meeting)
        self.meeting_job_service.add_saved_meetings_jobs(meeting)

    async def get_telegram_message(self, state: FSMContext):
        data = await state.get_data()
        meeting = data.get("meeting").get("entity")
        return self.meeting_assistant.compose_telegram_filling_message(meeting)
    
    def __unknown_user_to_json(self, unknown_user: UnknownUser):
        return json.dumps(unknown_user.__dict__)
    
    async def __get_company_code(self, chat_id: int):
        return await self.company_repository.get_company_code_by_chat_id(chat_id)
    
    async def __get_message_sender_full_name(self, user_id: int):
        return await self.user_repository.get_full_name_by_id(user_id=user_id)