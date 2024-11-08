from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class NotificationKeyboardBilder:
    @staticmethod
    def get_menu_filling_notification(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Изменить автора", callback_data="notification filling:author")],
                [InlineKeyboardButton(text="Изменить тему письма", callback_data="notification filling:topic")],
                [InlineKeyboardButton(text="Изменить текст письма", callback_data="notification filling:body")],
                [InlineKeyboardButton(text="Изменить приложения", callback_data="notification filling:attachments")],
                [InlineKeyboardButton(text="Изменить время отправки", callback_data="notification filling:delay")],
            ]
        )
        return keyboard
