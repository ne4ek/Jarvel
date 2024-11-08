from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_menu_main_page_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Постановщик задач", callback_data="group_go_to task_filling_main")],
            [InlineKeyboardButton(text="📅 Постановщик встреч", callback_data="group_go_to meeting_filling_main")],
            [InlineKeyboardButton(text="✉️ Рассылка сообщений", callback_data="group_go_to mail_filling_main")],
            [InlineKeyboardButton(text="ℹ️ Информация о чате", callback_data="group_go_to chat_info")],
            [InlineKeyboardButton(text="✏️ Редактировать чат", callback_data="group_go_to edit_chat_menu")],
        ]
    )
    return keyboard