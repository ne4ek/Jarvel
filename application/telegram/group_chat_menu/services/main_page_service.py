from application.telegram.handlers.group_chats.menu.keyboards.main_page_keyboards import get_menu_main_page_keyboard
from application.telegram.handlers.group_chats.menu.keyboards.edit_chat_keyboard import get_edit_chat_keyboard
from application.telegram.handlers.group_chats.menu.keyboards.chat_info_keyboard import get_go_to_main_menu_keyboard
from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.task import Task
from domain.entities.meeting import Meeting
from domain.entities.mail import Mail
from domain.contracts.assistant import Assistant
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

class MainPageService:
    def __init__(self, task_assistant: Assistant, mailing_assistant: Assistant, meeting_assistant: Assistant, repository_provider: RepositoriesDependencyProvider):
        self.task_assistant = task_assistant
        self.mailing_assistant = mailing_assistant
        self.meeting_assistant = meeting_assistant
        self.user_repository = repository_provider.get_users_repository()
        self.group_chat_repository = repository_provider.get_group_chats_repository()
        self.company_repository = repository_provider.get_companies_repository()
        
    def get_menu_main_page(self):
        text = "Главное меню"
        return {"text": text, "keyboard": get_menu_main_page_keyboard()}

    async def get_task_filling_menu(self, state: FSMContext, bot_message: Message, user_id: int):
        company_code = await self.company_repository.get_company_code_by_chat_id(bot_message.chat.id)
        task = Task()
        task.company_code = company_code
        task.author_user = await self.user_repository.get_by_id(user_id)
        await state.set_data({"task": {"entity": task, "message": bot_message}})
        return self.task_assistant.compose_telegram_filling_message(task, go_to_main_menu_button=True)
    
    async def get_meeting_filling_menu(self, state: FSMContext, bot_message: Message, user_id: int):
        company_code = await self.company_repository.get_company_code_by_chat_id(bot_message.chat.id)
        author_user = await self.user_repository.get_by_id(user_id)
        meeting = Meeting(company_code=company_code,
                          invitation_type="telegram",
                          author_user=author_user,
                          duration=30)
        await state.set_data({"meeting": {"entity": meeting, "message": bot_message}})
        return self.meeting_assistant.compose_telegram_filling_message(meeting, go_to_main_menu_button=True)
    
    async def get_mailing_filling_menu(self, state: FSMContext, bot_message: Message, user_id: int):
        company_code = await self.company_repository.get_company_code_by_chat_id(bot_message.chat.id)
        mail = Mail(company_code=company_code,
                    contact_type="telegram",
                    send_delay=1,
                    author_user=await self.user_repository.get_by_id(user_id))
        await state.set_data({"mail": {"entity": mail, "message": bot_message}})
        return self.mailing_assistant.compose_telegram_filling_message(mail, go_to_main_menu_button=True)
    
    async def get_info_menu(self, chat_id):
        group_chat_info_text = """Информация о чате {chat_name}

<u>Компания {company_name}</u>
Код компании: {company_code}
Описание:
{description}

Участники:
{participants}
"""
        group_chat = await self.group_chat_repository.get_by_chat_id(chat_id)
        company_name = await self.company_repository.get_name_by_company_code(group_chat.company_code)
        description = await self.company_repository.get_description_by_company_code(group_chat.company_code)
        participants_users = await self.company_repository.get_users_by_company_code(group_chat.company_code)
        participants_list = [f"{user.full_name} ({user.username})" for user in participants_users]
        text = group_chat_info_text.format(chat_name=group_chat.name, company_name=company_name,
                                           company_code=group_chat.company_code, description=description,
                                           participants="\n".join(participants_list))
        keyboard = get_go_to_main_menu_keyboard()
        return {"text": text, "keyboard": keyboard}
    
    async def get_edit_chat_menu(self, chat_id: int):
        group_chat = await self.group_chat_repository.get_by_chat_id(chat_id)
        is_group_registeres = await self.company_repository.is_group_registered_in_company(group_chat)
        if is_group_registeres:
            text = "В этом меню вы можете управлять чатом"
            keyboard = get_edit_chat_keyboard()
            return {"text": text, "keyboard": keyboard}
        else:
            text = "Для доступа к этому меню добавьте чат в компанию!"
            keyboard = get_go_to_main_menu_keyboard()
            return {"text": text, "keyboard": keyboard}
    
    async def delete_company_from_chat(self, chat_id: int):
        try:
            await self.group_chat_repository.delete(chat_id)
            text = "Вы успешно удалили чат из компании!\nДля привязки другой компании введите команду /add_chat_to_company"
            return {"text": text, "keyboard": None}
        except Exception as e:
            pass
            text = "Вы успешно удалили чат из компании! Для привязки другой компании введите команду /add_chat_to_company"
            return {"text": text, "keyboard": None}