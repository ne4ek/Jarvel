from aiogram import types, Router, F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from application.telegram.bot_msg.company_msg import join_company_not_found, join_owner_in_company, \
    join_company_success, join_company_role, join_company_role_exists
from application.telegram.models.state_forms import Registration
from db.postgresql_handlers.companies_db_handler import (
    get_code_from_companies,
    add_users_chat_in_company,
    is_user_in_chat_registered,
    add_user_id_in_company,
    get_users_id_from_company,
    get_owner_id_from_company,
)

router_user_registration = Router()
tag = "user_registration"


@router_user_registration.message(Command("join_company"), F.chat.type == "private")
async def company_registration_command(message: types.Message, state: FSMContext, command: CommandObject):
    """
    Function through which the user joins the company

    :param Message message: Object represents a message from Telegram
    :param FSMContext state: Object represents the state of the user
    :param Command command: Object represents a set of words sent by users after a command in a single message

    :return: None
    """
    if message.text == "/join_company":
        await message.reply(
            "Вы должны отправить только код коллектива через пробел после команды /join_company, пожалуйста отправьте код коллектива как в примере \n\n /join_company Stone "
        )
        return

    company_code = command.args
    # ic(command.args)
    if len(command.args.split()) != 1:
        await message.reply(
            "Вы должны отправить только код коллектива через пробел после команды /join_company, пожалуйста отправьте код коллектива как в примере \n\n /join_company Stone "
        )
        return

    if company_code not in get_code_from_companies():
        await message.reply(join_company_not_found.format(company_code))
        return

    if message.chat.id == get_owner_id_from_company(company_code):
        await message.reply(join_owner_in_company.format(company_code))

    elif message.chat.id in get_users_id_from_company(company_code):
        await message.reply(join_company_success.format(company_code))

    else:
        await state.update_data(company_code=company_code)
        await state.set_state(Registration.choosing_role)
        await message.reply(join_company_role.format(company_code))


@router_user_registration.message(Registration.choosing_role, F.chat.type == "private")
async def choosing_role(message: types.Message, state: FSMContext):
    """
    Function that prompts the user for their role in the company

    :param Message message: Object represents a message from telegram
    :param FSMContext state: Object represents the state of the user

    :return: None
    """
    data = await state.get_data()
    # ic(data)
    if not is_user_in_chat_registered(
        chat_id=message.chat.id, role=message.text, company_code=data["company_code"]
    ):
        add_users_chat_in_company(
            chat_id=message.chat.id,
            role=message.text,
            company_code=data["company_code"],
        )
        # TODO  add user_id in companies
        add_user_id_in_company(
            user_id=message.chat.id, company_code=data["company_code"]
        )
        await state.clear()
        await message.answer(join_company_success.format(data["company_code"]))

    else:
        await message.answer(join_company_role_exists.format(message.text))
