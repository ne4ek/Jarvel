from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from aiogram import types
from functools import wraps
from domain.entities.user_chat import UserChat
from icecream import ic

user_repository = repositroties_dependency_provider_async.get_users_repository()
company_repository = repositroties_dependency_provider_async.get_companies_repository()
group_chat_repository = repositroties_dependency_provider_async.get_group_chats_repository()
user_chat_repository = repositroties_dependency_provider_async.get_user_chats_repository()

def group_chat_callback_decorator(handler):
    #Decorator that checks user registration and group chat company registration
    @wraps(handler)
    async def wrapper(self, callback: types.CallbackQuery, *args, **kwargs):
        chat_id = callback.message.chat.id
        is_group_chat_aassigned_to_company = await group_chat_repository.is_group_chat_assigned_to_company(chat_id)
        if not is_group_chat_aassigned_to_company:
            await callback.message.edit_text(text="Данный групповой чат не привязан к компании.", reply_markup=None)
            return
        user_id = callback.from_user.id
        is_user_exists = await user_repository.is_user_exists(user_id)
        if not is_user_exists:
            await callback.message.edit_text(text="Пожалуйста, прежде чем использовать данный функционал, пройдите регистрации в личных сообщениях")
            return
        company_code = await group_chat_repository.get_company_code(chat_id)
        is_user_registered_in_company = await user_repository.is_user_registered_in_company(user_id, company_code)
        if not is_user_registered_in_company:
            await company_repository.add_user_id_by_company_code(user_id, company_code, role="не указана")
            await user_chat_repository.save_user_chat(UserChat(user_id=user_id,
                                                         role="не указана",
                                                         company_code=company_code))
        await handler(self, callback, *args, **kwargs)
    return wrapper