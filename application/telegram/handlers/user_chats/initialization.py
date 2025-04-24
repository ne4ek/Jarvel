from aiogram import Router

from infrastructure.config.user_chats.tasks.tasks_notifications_config import tasks_notification_router
from infrastructure.config.user_chats.meetings.meeting_notifications_config import meeting_notifications_router
from infrastructure.config.user_chats.user_registration_config import user_registration_router
from infrastructure.config.user_chats.companies.main_company_router import main_company_router
from infrastructure.config.user_chats.tasks.task_menu_config import task_menu_router, task_change_data_router
from infrastructure.config.user_chats.meetings.meeting_menu_config import meeting_menu_router
from infrastructure.config.user_chats.command_handlers import command_router
from infrastructure.config.user_chats.main_menu_config import main_menu_router
from infrastructure.config.user_chats.profile_menu_config import profile_menu_router
from infrastructure.config.user_chats.mailing_config import user_chat_mailing_router, user_chat_mail_inbox_router
from infrastructure.config.user_chats.compose_mailing_config import user_compose_mail_router
from infrastructure.config.user_chats.tunneling.tunneling_config import tunneling_menu_router
from application.messages.message_transcriber import transcribe_message_router

user_chats_router = Router()
user_chats_router.include_routers(
    command_router,
    user_compose_mail_router,
    profile_menu_router,
    meeting_notifications_router,
    tasks_notification_router,
    user_registration_router,
    main_company_router,
    task_menu_router,
    task_change_data_router,
    meeting_menu_router,
    main_menu_router,

    user_chat_mailing_router,
    user_chat_mail_inbox_router,
    tunneling_menu_router,
    transcribe_message_router,
)   
