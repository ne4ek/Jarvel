from aiogram import types, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from application.telegram.handlers.user_chats.user_chat_menu.main_menu_handlers import MainMenuHandlers


class UserChatCommandHandlers:
    def __init__(self, main_menu_message: MainMenuHandlers):
        self.main_menu_message = main_menu_message

    def get_router(self):
        router = Router()
        self.register_all_command_handlers(router)
        return router

    def register_all_command_handlers(self, router: Router):
        router.message(Command("main_menu"), F.chat.type == "private")(self.main_menu_command)

    async def start_command(self, message: types.Message):
        message.delete()
        await message.answer("Здесь обработка команды старт")
    
    async def main_menu_command(self, message: types.Message, state: FSMContext):
        await self.main_menu_message(message, state)