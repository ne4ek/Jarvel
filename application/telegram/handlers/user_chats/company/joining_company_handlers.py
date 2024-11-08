from application.companies.services.join_company_service import JoinCompanyService
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from domain.custom_errors.company_errors.invalid_company_length import InvalidCompanyLength
from domain.custom_errors.company_errors.company_code_not_found import CompanyCodeNotFound
from application.telegram.bot_msg import company_msg
from application.telegram.keyboards import user_chat_keyboards
from application.telegram.models.state_forms import JoinCompany
from domain.entities.user_chat import UserChat


class JoinCompanyHandlers:
    def __init__(self, companies_service: JoinCompanyService):
        self.companies_service = companies_service

    def get_router(self):
        router = Router()
        self.register_callback(router)
        self.register_handlers(router)
        return router


    def register_handlers(self, router: Router):
        router.message(JoinCompany.company_code, F.chat.type == "private")(self.join_company_company_code_handler)
        router.message(JoinCompany.choosing_role, F.chat.type == "private")(self.join_company_code_choosing_role_handler)

    def register_callback(self, router: Router):
        router.callback_query.register(self.join_company_callback, F.data == "user_join_company start")
        router.callback_query.register(self.join_company_callback, F.data == "user_join_company change_code")

    async def join_company_callback(self, callback: CallbackQuery, state: FSMContext):
        """
        Функция обрабатывает начало регистрации пользователя в новой компании

        :param CallbackQuery callback: Object represents a callback query from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """

        await state.set_state(JoinCompany.company_code)
        # company = Company()
        # await state.update_data(company=company)

        message = await callback.message.edit_text(text=company_msg.join_company_request_company_code,
                                                   reply_markup=user_chat_keyboards.menu_join_company_get_company_code())
        await state.update_data(message_to_edit_id=message.message_id)

    async def join_company_company_code_handler(self, message: Message, state: FSMContext):
        """
        Функция обрабатывает отправку кода компании для регистрации в компанию

        :param Message message: Object represents a message from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """

        data = await state.get_data()
        is_user_registered_in_company = await self.companies_service.is_user_registered_in_company(message.text, message.from_user.id)
        if is_user_registered_in_company:
            await message.delete()
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=data.get('message_to_edit_id'),
                                                text=company_msg.join_company_already_registered)
            await state.clear()
            return
        
        user_chat = self.companies_service.create_user_chat(message.chat.id)
        await state.update_data(user_chat=user_chat)
        company_code = message.text
        message_to_edit_id = data.get("message_to_edit_id")
        try:
            await self.companies_service.set_company_code(company_code, user_chat)
        except CompanyCodeNotFound:
            await message.bot.edit_message_text(text="Такого кода не существует", 
                                          chat_id=message.chat.id,
                                          message_id=message_to_edit_id)
            return
        except InvalidCompanyLength:
            await message.bot.edit_message_text(text="Неправильная длина кода",
                                          chat_id=message.chat.id,
                                          message_id=message_to_edit_id)
            return
        await message.bot.edit_message_text(text="Отлично! Теперь введите свою роль в коллективе",
                                            chat_id=message.chat.id,
                                            message_id=message_to_edit_id)
        await message.bot.delete_message(chat_id=message.from_user.id,
                                         message_id=message.message_id)
        await state.set_state(JoinCompany.choosing_role)

    async def join_company_code_choosing_role_handler(self, message: Message, state: FSMContext):
        """
        Фунцкия обрабатывает данные от пользователя о его роли в компании

        :param Message message: Object represents a message from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """
        data = await state.get_data()
        user_chat = data.get('user_chat')
        self.companies_service.set_role(role=message.text, user_chat=user_chat)
        is_user_registers = await self.companies_service.is_user_registered(user_chat)
        if is_user_registers:
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                               message_id=data.get('message_to_edit_id'),
                                                               text=company_msg.join_company_role_exists.format(
                                                                   message.text),
                                                               reply_markup=user_chat_keyboards.menu_join_company_check_company_code())
            return
        
        await self.companies_service.save_user(user_chat)
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=data.get('message_to_edit_id'),
                                            text=company_msg.join_company_success.format(
                                            data["user_chat"].company_code,
                                            message.text),
                                            reply_markup=user_chat_keyboards.menu_join_company_finally_message())
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await state.clear()
