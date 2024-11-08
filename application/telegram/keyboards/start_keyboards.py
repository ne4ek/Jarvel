from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Начать регистрацию", callback_data="start_user_registration")]]
    )
    return keyboard