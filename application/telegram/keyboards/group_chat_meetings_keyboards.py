from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder

from db.postgresql_handlers.companies_db_handler import get_company_name_from_company
from db.postgresql_handlers.users_db_handler import get_all_companies_from_user
from icecream import ic


go_to_menu_main_button = InlineKeyboardButton(text="Вернуться в главное меню", callback_data="group_go_to main_menu")


def get_menu_main():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Поставь новую встречу", callback_data="meeting_create start")],
            [InlineKeyboardButton(text="Изменить встречу", callback_data="meeting_refactor start")],
            [InlineKeyboardButton(text="Удалить встречу", callback_data="meeting_delete start")],
            [go_to_menu_main_button]
        ]
    )

    return keyboard


def get_menu_meeting_filling_keyboard(data_completely_filled=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    if data_completely_filled:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Сохранить встречу", callback_data="meeting_save")])

    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="Изменить тему встречи", callback_data="meeting_filling_change topic")],
        [InlineKeyboardButton(text="Изменить время встречи", callback_data="meeting_filling_change meeting_time")],
        [InlineKeyboardButton(text="Изменить время напоминания до встречи",
                              callback_data="meeting_filling_change remind_time")],
        [InlineKeyboardButton(text="Изменить модератора встречи", callback_data="meeting_filling_change moderator")],
        [InlineKeyboardButton(text="Изменить участников", callback_data="meeting_filling_change participants")],
        [InlineKeyboardButton(text="Изменить ссылку", callback_data="meeting_filling_change link")],
        [InlineKeyboardButton(text="Изменить тип напоминания", callback_data="meeting_filling_change invitation_type")],
        [InlineKeyboardButton(text="Изменить продолжительность встречи", callback_data="meeting_filling_change duration")],
        [InlineKeyboardButton(text="Удалить", callback_data="meeting_filling_delete")],
        [go_to_menu_main_button]
    ])
    return keyboard


go_to_menu_meetings_filling_button = InlineKeyboardButton(text="Вернуться к заполнению встречи",
                                                          callback_data="meeting_go_to menu_meeting_filling")


def get_go_to_menu_meetings_filling():
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_meetings_filling_button],
        ]
    )
    return button


def get_go_to_menu_main():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_main_button],
        ]
    )
    return keyboard


def get_invitation_type_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Telegram', callback_data='invitation_type telegram')],
            [InlineKeyboardButton(text='Email', callback_data='invitation_type email')],
            [go_to_menu_meetings_filling_button]
        ]
    )
    return keyboard


def get_go_to_menu_meetings_filling():
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_meetings_filling_button],
        ]
    )
    return button


def get_go_to_menu_main():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_main_button],
        ]
    )
    return keyboard


def get_invitation_type_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Telegram', callback_data='invitation_type telegram')],
            [InlineKeyboardButton(text='Email', callback_data='invitation_type email')],
            [go_to_menu_meetings_filling_button]
        ]
    )
    # 
    # back_button = get_go_to_menu_meetings_filling()
    # buttons.inline_keyboard.append(back_button.inline_keyboard[0])
    # 
    return keyboard

