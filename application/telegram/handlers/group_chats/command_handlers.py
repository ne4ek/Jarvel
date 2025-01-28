from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.postgresql_handlers.companies_db_handler import get_code_owner_from_company
from infrastructure.config.repository_provider_async_config import companies_repository, tunneling_repository
from domain.entities.group_chat import GroupChat
from icecream import ic
from domain.entities.tunneling_message import TunnelingMessage

import re

router_commands = Router()

class AddChatToCompanyStates(StatesGroup):
    waiting_for_company_code = State()
    
class TunnelState(StatesGroup):
    waiting_for_link = State()

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

@router_commands.message(Command("registration"), F.chat.type != "private")
async def add_chat_to_company_start(message: Message, state: FSMContext):
    await message.reply("Регистрация проходит в личных сообщениях бота.")


@router_commands.message(Command("tunnel"), F.chat.type != "private")
async def add_chat_to_company_start(message: Message, state: FSMContext):
    await message.reply("Отправьте ссылку на чат.")
    await state.set_state(TunnelState.waiting_for_link)


@router_commands.message(TunnelState.waiting_for_link, F.chat.type != "private")
async def add_chat_to_company_process(message: Message, state: FSMContext):
    link = message.text.strip()
    ic(link)
    if not is_telegram_link(link):
        await message.reply("Это не выглядит как ссылка на чат.")
    else:
        bot = message.bot
        splited_link = link.split("/")
        if splited_link[-2].isdigit():
            to_chat_id = int("-100" + splited_link[-2])
            to_topic_id = int(splited_link[-1])
            if to_topic_id == 1:
                to_topic_id = 0
        else:
            to_chat_id = int("-100" + splited_link[-1])
            to_topic_id = None
        from_chat_id = int("-100" + str(abs(message.chat.id)))
        from_topic_id = message.message_thread_id 
        tunneling_message = TunnelingMessage(to_chat_id=to_chat_id, to_topic_id=to_topic_id,
                         from_chat_id=from_chat_id, from_topic_id=from_topic_id) 
        ic(tunneling_message)
        await tunneling_repository.save(tunneling_message)
        await bot.send_message(chat_id=to_chat_id, text="aboba", message_thread_id=to_topic_id)
    await state.clear()
    
    

def is_telegram_link(url: str):
    pattern = r"https://t\.me/[+\w\-_/]+"
    return re.match(pattern, url)
    