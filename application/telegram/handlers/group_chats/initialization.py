from aiogram import Router

from application.telegram.handlers.group_chats.command_handlers import router_commands
from infrastructure.config.telegram_messages_config import messages_router
from infrastructure.config.group_chats.tasks_group_chat_config import task_router
from infrastructure.config.group_chats.mailing_group_chat_config import compose_mail_router
from infrastructure.config.meeting_group_chat_config import meeting_router
from infrastructure.config.group_chats.main_menu_handlers import main_menu_router
from infrastructure.config.tunneling_config import tunneling_router

# from application.telegram.handlers import router_commands
# from application.telegram.handlers import router_messages

group_chats_router = Router()

group_chats_router.include_routers(
    router_commands,
    main_menu_router,
    task_router,
    meeting_router,
    compose_mail_router,
    tunneling_router,
    messages_router,
    )
