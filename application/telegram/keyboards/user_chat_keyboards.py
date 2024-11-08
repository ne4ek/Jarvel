from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import CallbackData, InlineKeyboardBuilder

from db.postgresql_handlers.companies_db_handler import get_company_name_from_company
from db.postgresql_handlers.users_db_handler import get_all_companies_from_user
from icecream import ic


go_to_menu_main_button = InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")


def get_companies_builder(user_id: int, next_stage: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    companies_codes = get_all_companies_from_user(user_id)
    for company_code in companies_codes:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=get_company_name_from_company(company_code),
                                  callback_data=f"user_go_to menu_{next_stage} company_code:{company_code}")]
        )
        # ic(keyboard)

    keyboard.inline_keyboard.append([go_to_menu_main_button])
    return keyboard


def menu_join_company_get_company_code():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_join_company_check_company_code():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="Подтвердить", callback_data="user_join_company save_code")],
            [InlineKeyboardButton(text="Изменить код компании", callback_data="user_join_company change_code")],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_join_company_finally_message():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_main_button]
        ]
    )
    return keyboard










def menu_create_company_set_company_name():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="Вернуться в профиль", callback_data='go_to menu_profile')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_create_company_set_company_topic():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить название", callback_data='user_create_company start')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_create_company_final_check():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Изменить название", callback_data='user_create_company change_name'),
             InlineKeyboardButton(text="Изменить описание", callback_data='user_create_company change_description')],
            [InlineKeyboardButton(text="Сохранить компанию", callback_data='user_create_company save_company')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


def menu_create_company_final_message():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            # [InlineKeyboardButton(text="", callback_data='user_create_company start')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard

def menu_create_company_change_data():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться без изменений", callback_data='user_create_company preview')],
            [go_to_menu_main_button]
        ]
    )
    return keyboard


# def menu_change_personal_link_finnaly():
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="Вернуться в профиль", callback_callback='go_to menu_profile')],
#             [go_to_menu_main_button()]
#         ]
#     )
#     return keyboard


def start_keyboard() -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1) Суммаризация ГС", callback_data="start_1")],
            [
                InlineKeyboardButton(
                    text="2) Контроль сообщений", callback_data="start_2"
                )
            ],
            [InlineKeyboardButton(text="3) Постановка задач", callback_data="start_3")],
            # [InlineKeyboardButton(text="4) Ответы на вопросы", callback_data="start_4")]
        ]
    )

    return buttons


def back_to_start_keyboard() -> InlineKeyboardMarkup:
    button = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="<<", callback_data="start_0")]]
    )

    return button













































