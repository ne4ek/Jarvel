from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class UserChatInboxService:
    def __init__(self):
        pass
    
    async def get_mail_inbox_menu(self, state):
        data = await state.get_data()
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu"),
                                                          InlineKeyboardButton(text="В меню почты", callback_data=f"user_go_to mail_menu_company_code:{data.get('company_code')}")]])
        return {"text": "Данное меню находится в разработке", "keyboard": keyboard}