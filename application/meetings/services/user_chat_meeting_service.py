from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.meeting import Meeting
from .telegram_meeting_notification_service import SendTelegramMeetingNotificationService
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

class UserChatMeetingService:
    def __init__(self, repositories: RepositoriesDependencyProvider, meeting_notification_service: SendTelegramMeetingNotificationService):
        self.meeting_repository = repositories.get_meetings_repository()
        self.user_repository = repositories.get_users_repository()
        self.meeting_notification_service = meeting_notification_service
    
    def participant_meeting_accepted(self) -> dict:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        text = f"Отлично! Я напомню вам о встрече до ее начала!"
        return {"text": text, "keyboard": keyboard}
    
    async def participant_meeting_declined(self, meeting_id: int, user_id: int) -> dict:
        meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        text = \
'''
Принято. Я оповещу модератора встречи о вашем решении.
'''
        meeting.participants_id.remove(user_id)
        declined_user = await self.user_repository.get_by_id(user_id)
        await self.meeting_repository.set_participants(meeting.participants_id, meeting_id)
        await self.meeting_notification_service.send_moderator_user_declined_participation(meeting, declined_user)
        return {"text": text, "keyboard": keyboard}

    async def moderator_update_link(self, meeting_id: int, link: str) -> dict:
        await self.meeting_repository.set_link(meeting_id, link)
        meeting = await self.meeting_repository.get_by_meeting_id(meeting_id)
        participants_users: dict = meeting.participants_users
        invitation_type = meeting.invitation_type
        topic = meeting.topic
        duration = meeting.duration
        link = meeting.link if meeting.link else "не указана"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Изменить ссылку", callback_data=f"moderator_set_link meeting_id:{meeting_id}")],
                    [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]
                ])
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
        return {"text": moderator_text, "keyboard": keyboard}