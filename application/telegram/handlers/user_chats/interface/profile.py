from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram import Router
from application.telegram.bot_msg.user_profile import profile_summary, companies_where_user_owner_text, \
    companies_where_user_participant_text, change_personal_link, change_email
from application.telegram.keyboards import user_chat_profile_keyboards

from application.telegram.models.state_forms import PersonalLinkChange, PersonalEmailChange
from db.postgresql_handlers.companies_db_handler import get_all_companies_names_where_user_owner, get_all_companies_names_from_company_by_user
from icecream import ic


import re

router_companies = Router()


async def menu_profile_callback(callback: CallbackQuery, state: FSMContext):
    """Функция выводит главное меню профиля человека"""

    await state.clear()

    data = get_all_from_user(callback.message.chat.id)
    companies_where_user_participant = get_all_companies_names_from_company_by_user(callback.message.chat.id)
    companies_where_user_owner = get_all_companies_names_where_user_owner(callback.message.chat.id)
    ic(companies_where_user_participant)
    ic(companies_where_user_owner)

    text = profile_summary.format(
        name=data.get('name'),
        email=data.get('email'),
        link=data.get('personal_link') if data.get('personal_link') is not None else "Отсутствует",
    )

    if companies_where_user_owner:
        text += companies_where_user_owner_text.format(', '.join(companies_where_user_owner))

    if companies_where_user_participant:
        text += companies_where_user_participant_text.format(', '.join(companies_where_user_participant))

    await callback.message.edit_text(text=text, reply_markup=user_chat_profile_keyboards.menu_profile(), disable_web_page_preview=True)


async def change_user_link_callback(callback: CallbackQuery, state: FSMContext):
    """Функция начинает изменение личной ссылки пользователя на встречи в бд"""

    old_message = await callback.message.edit_text(text=change_personal_link, reply_markup=user_chat_profile_keyboards.menu_change_personal_link())
    await state.update_data(message_to_edit=old_message.message_id)
    await state.set_state(PersonalLinkChange.personal_link)


@router_companies.message(PersonalLinkChange.personal_link)
async def change_user_link_handler(message: Message, state: FSMContext):
    """Функция обрабатывает только что полученную ссылку"""

    pattern_check_is_link = re.compile(
        r'((http|https):\/\/)?(www\.)?[a-zA-Z0-9\-_]+\.[a-zA-Z]{2,}(\.[a-zA-Z]{2,})?(\/[a-zA-Z0-9\-_]+)*(\/[a-zA-Z0-9\-_]+\.[a-zA-Z]{2,})?(\?[a-zA-Z0-9=&]+)?')


    data = await state.get_data()
    text = ""
    if bool(pattern_check_is_link.search(message.text)):
        save_personal_link(message.chat.id, message.text)
        text = "Ваша ссылка успешно сохранена."
        await state.clear()
    else:
        text = "Неправильный формат ссылки. Пожалуйста введите её ещё раз"

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=data['message_to_edit'],
                                    text=text,
                                    reply_markup=user_chat_profile_keyboards.menu_change_personal_link())
    except:
        pass


async def change_user_email_callback(callback: CallbackQuery, state: FSMContext):
    """Функция начинает изменение email пользователя в бд"""

    old_message = await callback.message.edit_text(text=change_email, reply_markup=user_chat_profile_keyboards.menu_change_email())
    await state.update_data(message_to_edit=old_message.message_id)
    await state.set_state(PersonalEmailChange.email)



@router_companies.message(PersonalEmailChange.email)
async def change_user_email_handler(message: Message, state: FSMContext):
    """Функция обрабатывает только что полученный email"""

    pattern_check_is_email = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    data = await state.get_data()
    text = ""
    if bool(pattern_check_is_email.search(message.text)):
        save_email(message.chat.id, message.text)
        # save_personal_link(message.chat.id, message.text)
        text = "Ваш email успешно сохранен."
        await state.clear()
    else:
        text = "Неправильный формат email. Пожалуйста введите вашу почу ещё раз"

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    try:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=data['message_to_edit'],
                                    text=text,
                                    reply_markup=user_chat_profile_keyboards.menu_change_personal_link())
    except:
        pass
