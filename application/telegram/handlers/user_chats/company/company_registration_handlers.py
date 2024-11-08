from application.companies.services.create_company_service import CreateCompanyService
from aiogram import Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from application.telegram.bot_msg import company_msg
from application.telegram.keyboards import user_chat_keyboards
from application.telegram.models.state_forms import CompanyCreation


class CreateCompanyHandler:
    def __init__(self, companies_service: CreateCompanyService):
        self.companies_service = companies_service

    def get_router(self):
        router = Router()
        self.register_callback(router)
        self.register_handlers(router)
        return router

    def register_handlers(self, router: Router):
        router.message(CompanyCreation.choosing_company_name, F.chat.type == "private", F.text)(
            self.choosing_new_company_name)
        router.message(CompanyCreation.choosing_company_description, F.chat.type == "private",
                       F.text)(self.choosing_new_company_description)
        return router

    def register_callback(self, router: Router):
        router.callback_query.register(self.menu_create_company_callback,
                                   F.data == "user_create_company start")

        router.callback_query.register(self.save_new_company_callback,
                                   F.data == "user_create_company save_company")

        router.callback_query.register(self.change_company_name,
                                   F.data == "user_create_company change_name")

        router.callback_query.register(self.change_company_description,
                                   F.data == "user_create_company change_description")

        router.callback_query.register(self.preview_of_final_version_of_new_company_callback,
                                   F.data == "user_create_company preview")

    async def menu_create_company_callback(self, callback: CallbackQuery, state: FSMContext):
        """
        Функция начинает процесс создания новой компании

        :param CallbackQuery callback: Object represents a callback query from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """
        await state.set_state(CompanyCreation.choosing_company_name)
        company = self.companies_service.create_company()

        await state.update_data(company=company)

        message_to_edit = await callback.message.edit_text(text=company_msg.create_company_set_new_name,
                                                           reply_markup=user_chat_keyboards.menu_create_company_set_company_name())
        await state.update_data(message_to_edit=message_to_edit.message_id)

    async def change_company_name(self, callback: CallbackQuery, state: FSMContext):
        """
        Функция выводит сообщение с просьбой ввести новое название компании

        :param CallbackQuery callback: Object represents a callback query from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """
        await state.set_state(CompanyCreation.choosing_company_name)

        await callback.message.edit_text(text=company_msg.create_company_change_name,
                                         reply_markup=user_chat_keyboards.menu_create_company_change_data())

    async def change_company_description(self, callback: CallbackQuery, state: FSMContext):
        """
        Функция выводит сообщение с просьбой ввести новое описание компании

        :param CallbackQuery callback: Object represents a callback query from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """
        await state.set_state(CompanyCreation.choosing_company_description)

        await callback.message.edit_text(text=company_msg.create_company_change_description,
                                         reply_markup=user_chat_keyboards.menu_create_company_change_data())

    async def choosing_new_company_name(self, message: Message, state: FSMContext):
        """
        Function processes the selection of a name for the team

        :param Message message: Object represents a message from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """
        
        data = await state.get_data()
        company = data.get('company')
        company_name = message.text
        self.companies_service.set_company_name(company_name, company)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        
        if company.description is None:
            await state.set_state(CompanyCreation.choosing_company_description)
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                               message_id=data.get('message_to_edit'),
                                                               text=company_msg.create_company_set_new_description.format(
                                                                   company_name=company_name),
                                                               reply_markup=user_chat_keyboards.menu_create_company_set_company_topic())
        else:
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                               message_id=data['message_to_edit'],
                                                               reply_markup=user_chat_keyboards.menu_create_company_final_check(),
                                                               text=company_msg.create_company_final_check_text.format(
                                                                   name=company.name,
                                                                   description=company.description
                                                               ))


    async def choosing_new_company_description(self, message: Message, state: FSMContext):
        """
        Function for processing the description of a team and saving it to the database

        :param Message message: Object represents a message from Telegram
        :param FSMContext state: Object represents the state of the user
        :return: None
        """
        data = await state.get_data()
        company = data.get('company')
        # await state.update_data(description=message.text)
        self.companies_service.set_company_description(message.text, company)

        data = await state.get_data()

        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.bot.edit_message_text(chat_id=message.chat.id, message_id=data['message_to_edit'],
                                                           reply_markup=user_chat_keyboards.menu_create_company_final_check(),
                                                           text=company_msg.create_company_final_check_text.format(
                                                               name=company.name,
                                                               description=company.description
                                                           ))

    async def save_new_company_callback(self, callback: CallbackQuery, state: FSMContext):
        """
        Функция сохраняет новую компанию

        :param CallbackQuery callback: Object represents a callback query from Telegram
        :param FSMContext state: Object represents the state of the user
        """

        data = await state.get_data()
        company = data.get('company')
        await self.companies_service.set_company_code(code=None, company=company)
        self.companies_service.set_company_owner_id(callback.message.chat.id, company)

        await self.companies_service.save(company)

        await callback.message.edit_text(text=company_msg.create_company_save_new_company.format(
            company_name=company.name, company_code=company.code),
            reply_markup=user_chat_keyboards.menu_create_company_final_message()
        )
        await state.clear()

    async def preview_of_final_version_of_new_company_callback(self, callback: CallbackQuery, state: FSMContext):
        """
        Функция выводит уже известную информацию о новой компании через callback
        :param CallbackQuery callback: Object represents a callback query from Telegram
        :param FSMContext state: Object represents the state of the user

        :return: None
        """

        data = await state.get_data()
        company = data.get('company')
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                             message_id=data['message_to_edit'],
                                             reply_markup=user_chat_keyboards.menu_create_company_final_check(),
                                             text=company_msg.create_company_final_check_text.format(
                                             name=company.name,
                                             description=company.description
                                            ))
