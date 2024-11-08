from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from application.telegram.keyboards.user_chat_keyboards import go_to_menu_main_button


def menu_profile():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить имя и фамилию", callback_data="user_profile change_name")],
            [InlineKeyboardButton(text="Изменить почту", callback_data="user_profile change_email")],
            [InlineKeyboardButton(text="Изменить личную ссылку для встреч", callback_data="user_profile change_link")],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_change_personal_link():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться в профиль", callback_data='user_go_to menu_profile')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_change_email():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться в профиль", callback_data='user_go_to menu_profile')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard