from aiogram import types, F, Router
from aiogram.filters import Command, CommandObject
#Now this class does not use
class GroupChatCommandHandlers:
    def __init__(self, main_menu_keyboard: types.InlineKeyboardMarkup):
        self.main_menu_keyboard = main_menu_keyboard

    def register_all_command_handlers(self):
        router = Router()
        router.message(Command("add_chat_to_company"), F.chat.type != "private")(self.add_chat_to_company_command)
        router.message(Command("main_menu"), F.chat.type != "private")(self.main_menu_command)

    async def add_chat_to_company_command(self, message: types.Message, command: CommandObject):
        company_code = command.args
        
        response = self.add_chat_to_company.execute(message, company_code)
        
        await message.reply(response)

    async def main_menu_command(self, message: types.Message):
        text = "Главное меню"
        
        await message.answer(text=text, reply_markup=self.main_menu_keyboard)
        