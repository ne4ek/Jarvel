from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


go_to_group_menu_main = InlineKeyboardButton(text="В главное меню", callback_data="group_go_to main_menu")

def get_go_to_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[go_to_group_menu_main]])