from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.postgresql_handlers.companies_db_handler import get_code_owner_from_company
from infrastructure.config.repository_provider_async_config import companies_repository
from domain.entities.group_chat import GroupChat

router_commands = Router()

class AddChatToCompanyStates(StatesGroup):
    waiting_for_company_code = State()

@router_commands.message(Command("add_chat_to_company"), F.chat.type != "private")
async def add_chat_to_company_start(message: Message, state: FSMContext):
    chat_id = message.chat.id
    chat_name = message.chat.full_name
    is_group_in_company_registered = await companies_repository.get_company_code_by_chat_id(chat_id)

    if is_group_in_company_registered:
        await message.reply("Чат уже добавлен в компанию!")
        return

    await message.reply("Введите код компании для добавления чата\n(например: <code>Belomorie</code> ):", parse_mode="HTML")
    await state.set_state(AddChatToCompanyStates.waiting_for_company_code)

@router_commands.message(AddChatToCompanyStates.waiting_for_company_code, F.chat.type != "private")
async def add_chat_to_company_process(message: Message, state: FSMContext):
    company_code = message.text.strip()
    chat_id = message.chat.id
    chat_name = message.chat.full_name

    data = get_code_owner_from_company(company_code)

    if not data:
        await message.reply(f"Компании с кодом {company_code} не найдено! Попробуйте снова.")
        return

    gc = GroupChat(chat_id=chat_id, company_code=company_code, name=chat_name)
    
    await companies_repository.add_group_chat_to_company(gc)
    await message.reply("Чат добавлен в компанию!")
    await state.clear()

