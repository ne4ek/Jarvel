from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.context import FSMContext
from application.providers.repositories_provider import RepositoriesDependencyProvider
from application.telegram.models.state_forms import PersonalInfoChange
import re
from icecream import ic

class ProfileMenuService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider):
        self.user_chat_repository = repository_provider.get_user_chats_repository()
        self.companies_repository = repository_provider.get_companies_repository()
        self.users_repository = repository_provider.get_users_repository()
    
    async def profile_menu_start(self, user_id: int):
        user = await self.users_repository.get_by_id(user_id)
        user_name = user.full_name
        user_email = user.email
        text = \
'''
Профиль:
Имя: {user_name}
Почта: {user_email}
'''
        text = text.format(user_name=user_name, user_email=user_email)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить имя", callback_data="user_go_to change_name"),
                InlineKeyboardButton(text="Изменить почту", callback_data="user_go_to change_email"),
            ],
            [
                InlineKeyboardButton(text="Мои коллективы", callback_data="user_go_to my_companies"),
            ],
            [
                InlineKeyboardButton(text="Назад", callback_data="user_go_to main_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    
    def profile_menu_change_name(self):
        text = "Введите новое имя (без фамилии):"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Отменить смену имени", callback_data="user_go_to profile_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    
    def profile_menu_change_lastname(self):
        text = "Теперь введите новую фамилию:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Отменить смену имени", callback_data="user_go_to profile_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    
    def profile_menu_get_change_name_confirmation(self, new_first_name: str, new_lastname: str):
        text = "Новое имя: {new_first_name}\nНовая фамилия: {new_lastname}\n\nПодтвердите изменение"
        text = text.format(new_first_name=new_first_name,
                           new_lastname=new_lastname)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Подтвердить", callback_data="user_change_name confirm")],
                [InlineKeyboardButton(text="Изменить имя", callback_data="user_go_to change_name"), InlineKeyboardButton(text="Изменить фамилию", callback_data="user_go_to change_lastname")],
                [InlineKeyboardButton(text="Отменить смену имени", callback_data="user_go_to profile_menu")]
            ])
        return {"text": text, "keyboard": keyboard}
    
    async def update_name(self, user_id: int, new_first_name: str, new_lastname: str):
        user = await self.users_repository.get_by_id(user_id)
        user.first_name = new_first_name
        user.last_name = new_lastname
        await self.users_repository.update(user)
        text = "Имя успешно изменено!\nНовое имя: {new_first_name}\nНовая фамилия: {new_lastname}"
        text = text.format(new_first_name=new_first_name, new_lastname=new_lastname)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Вернуться в профиль", callback_data="user_go_to profile_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    
    def profile_menu_change_email(self):
        text = "Введите новую почту:"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Отменить смену почты", callback_data="user_go_to profile_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    
    async def profile_menu_get_change_email_confirmation(self, state: FSMContext, new_email: str):
        text = "Новая почта: {new_email}\n\nПодтвердите изменение"
        pattern_check_is_email = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        if bool(pattern_check_is_email.search(new_email)):
            await state.set_state(PersonalInfoChange.empty)
            await state.update_data({"new_email": new_email})
            text = text.format(new_email=new_email)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Подтвердить", callback_data="user_change_email confirm")],
                    [InlineKeyboardButton(text="Изменить почту", callback_data="user_go_to change_email")],
                    [InlineKeyboardButton(text="Отменить смену почты", callback_data="user_go_to profile_menu")]
                ])
            return {"text": text, "keyboard": keyboard}
        else:
            text = "Неправильный формат email. Пожалуйста введите вашу почту ещё раз"
            state.set_state(PersonalInfoChange.choosing_email)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Отменить смену почты", callback_data="user_go_to profile_menu")]
            ])
            return {"text": text, "keyboard": keyboard}

    async def update_email(self, user_id: int, new_email: str):
        user = await self.users_repository.get_by_id(user_id)
        user.email = new_email
        await self.users_repository.update(user)
        text = "Почта успешно изменена!\nНовая почта: {new_email}"
        text = text.format(new_email=new_email)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Вернуться в профиль", callback_data="user_go_to profile_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    

    async def profile_menu_my_companies(self, user_id: int):
        text = await self.__get_text_for_profile_menu_my_companies(user_id)
        ic(text)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="Вернуться в профиль", callback_data="user_go_to profile_menu"),
            ]
        ])
        return {"text": text, "keyboard": keyboard}
    

    async def __get_text_for_profile_menu_my_companies(self, user_id: int):
        text = ""

        company_names_and_codes_user_role_owner = await self.companies_repository.get_companies_names_and_codes_by_user_id_role_owner(user_id)
        company_names_and_codes_user_role_user = await self.companies_repository.get_companies_names_and_codes_by_user_id_role_user(user_id)

        if company_names_and_codes_user_role_owner:
            text += "Вы создатель: \n\n"
            text = self.__set_company_info_in_text_profile_menu_my_companies(company_names_and_codes_user_role_owner, text)
        if company_names_and_codes_user_role_user:
            if text :
                text += "--------------------------------\n"
            text += "Вы участник: \n\n"
            text = self.__set_company_info_in_text_profile_menu_my_companies(company_names_and_codes_user_role_user, text)
        if not text:
            text += "У вас нет коллективов"
        return text
    
    def __set_company_info_in_text_profile_menu_my_companies(self, company_names_and_codes, text_for_extension):
        for company_name_and_code in company_names_and_codes:
            text_for_extension += f"<b>Название</b> - {company_name_and_code[0]}\n<b>Код</b> - <code>{company_name_and_code[1]}</code>\n\n"
        return text_for_extension
