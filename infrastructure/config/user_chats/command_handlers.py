from application.telegram.handlers.user_chats.commands.commands_handlers import UserChatCommandHandlers
from infrastructure.config.user_chats.main_menu_config import main_menu_handlers

command_handlers = UserChatCommandHandlers(main_menu_handlers)

command_router = command_handlers.get_router()