from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои задачи", callback_data="user_go_to tasks_choose_company")],
            [InlineKeyboardButton(text="📅 Мои встречи", callback_data="user_go_to meet_choose_company")],
            [InlineKeyboardButton(text="✉️ Моя почта", callback_data="user_go_to mail_choose_company")],
            [InlineKeyboardButton(text="🏢 Создать команду", callback_data="user_create_company start")],
            [InlineKeyboardButton(text="🤝 Присоединиться к команде", callback_data="user_join_company start")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="user_go_to profile_menu")],
        ]
    )
    return keyboard