from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder

# from db.postgresql_handlers.companies_db_handler import get_company_name_from_company
# from db.postgresql_handlers.users_db_handler import get_all_companies_from_user
from icecream import ic


go_to_group_menu_main = InlineKeyboardButton(text="В главное меню", callback_data="group_go_to main_menu")


def get_menu_main():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Постановщик задач group", callback_data="group_go_to menu_manager_task")],
            [InlineKeyboardButton(text="📅 Постановщик встреч", callback_data="group_go_to menu_manager_meeting")],
            [InlineKeyboardButton(text="ℹ️ Информация о чате", callback_data="group_go_to menu_chat_info")],
            [InlineKeyboardButton(text="✏️ Редактировать чат", callback_data="group_go_to menu_refactor_chat")],
            [InlineKeyboardButton(text="Рассылка", callback_data="group_go_to menu_mailing")]
        ]
    )
    return keyboard

def get_menu_group_chat_info():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_group_menu_main],
        ]
    )
    return keyboard


def get_menu_group_chat_refactor():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Удалить компанию из чата", callback_data="group_delete_company_from_chat")],
            [go_to_group_menu_main],
        ]
    )
    return keyboard


def get_after_delete_company_from_chat_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_group_menu_main],
        ]
    )
    return keyboard


