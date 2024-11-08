from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from application.telegram.keyboards.keybords_paginators import MeetingsListPaginator, CompaniesPaginator, MenuMeetingsPaginator
from application.telegram.keyboards.user_chat_keyboards import go_to_menu_main_button
from db.postgresql_handlers.companies_db_handler import get_company_name_from_company
from db.postgresql_handlers.meetings_db_handler import get_last_n_meetings_by_user
from db.postgresql_handlers.users_db_handler import get_all_companies_from_user
from icecream import ic


def get_meetings_companies_builder(user_id: int):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    companies_codes = get_all_companies_from_user(user_id)
    for company_code in companies_codes:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=get_company_name_from_company(company_code),
                                  callback_data=MenuMeetingsPaginator(company_code=company_code).pack())]
        )

    keyboard.inline_keyboard.append([go_to_menu_main_button])
    return keyboard


def get_builder_meetings_list(user_id, company_code):
    data = get_last_n_meetings_by_user(user_id=user_id, n=5)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[]
    )
    for i, item in enumerate(data):
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=f"{i + 1}. {item.get('topic')}",
                                  callback_data=MeetingsListPaginator(
                                      meeting_id=item.get('meeting_id'),
                                      company_code=company_code).pack())
             ]
        )
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="По времени встречи", callback_data=CompaniesPaginator(
            company_code=company_code,
            tasks_type="meetings",
            sort_type="deadline").pack())])

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="К выбору компании", callback_data="user_go_to choose_company_meetings")])
    keyboard.inline_keyboard.append([go_to_menu_main_button])
    return keyboard


def get_one_meeting_keyboard(company_code):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Вернуться к списку всех встреч",
                                  callback_data=MenuMeetingsPaginator(company_code=company_code).pack())],
            [go_to_menu_main_button]
        ]
    )
    return keyboard
# def get_one_meetin
