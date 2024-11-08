from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

go_to_group_menu_main = InlineKeyboardButton(text="В главное меню", callback_data="group_go_to main_menu")

def get_edit_chat_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Удалить компанию из чата", callback_data="group_delete_company_from_chat")],
            [go_to_group_menu_main],
        ]
    )
    return keyboard