import aiogram
from aiogram.fsm.context import FSMContext
from aiogram import types, Router, F
from application.mailing.services.telegram_compose_mailing_service import TelegramComposeMailService
from application.telegram.handlers.group_chats.mailing.kayboards.compose_mailing_keyboard import get_go_to_mailing_filling_keyboard, get_mailing_filling_contact_type_keyboard, get_go_to_main_menu_keyboard
from application.telegram.models.state_forms import MailingState
from application.messages.message_transcriber import audio_to_text_converter
from application.telegram.decorators import group_chat_callback_decorator

class ComposeMailHandlers():
    def __init__(self, mailing_service: TelegramComposeMailService):
        self.mailing_service = mailing_service

    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_handlers(router)
        return router

    def __register_handlers(self, router: Router) -> None:
        router.message(MailingState.change_author, F.chat.type != "private")(self.change_mail_author_state)
        router.message(MailingState.change_topic, F.chat.type != "private")(self.change_mail_topic_state)
        router.message(MailingState.change_body, F.chat.type != "private")(self.change_mail_body_state)
        router.message(MailingState.change_recipients, F.chat.type != "private")(self.change_mail_recipients_state)
        router.message(MailingState.change_attachment, F.chat.type != "private")(self.change_mail_attachment_state)
        router.message(MailingState.change_send_delay, F.chat.type != "private")(self.change_mail_sending_delay_state)

    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.change_mail_author_callback, F.message.chat.type != "private", F.data == "mailing_filling_change author")
        router.callback_query.register(self.change_mail_topic_callback, F.message.chat.type != "private",  F.data == "mailing_filling_change topic")
        router.callback_query.register(self.change_mail_body_callback, F.message.chat.type != "private",  F.data == "mailing_filling_change body")
        router.callback_query.register(self.change_mail_recipients_callback, F.message.chat.type != "private", 
                                       F.data == "mailing_filling_change recipients")
        router.callback_query.register(self.change_mail_attachment_callback, F.message.chat.type != "private", 
                                       F.data == "mailing_filling_change attachment")
        router.callback_query.register(self.delete_mailing_callback, F.message.chat.type != "private", F.data == "mailing_delete")
        router.callback_query.register(self.go_back_to_filling_callback, F.message.chat.type != "private", F.data == "mailing_filling back")
        router.callback_query.register(self.delete_mailing_callback, F.message.chat.type != "private", F.data == "mailing_filling_delete")
        router.callback_query.register(self.change_mail_contact_type_callback, F.message.chat.type != "private", F.data == "mailing_filling_change contact_type")
        router.callback_query.register(self.set_email_contact_type_callback, F.message.chat.type != "private", F.data == "mailing_filling contact_email")
        router.callback_query.register(self.set_telegram_contact_type_callback, F.message.chat.type != "private", F.data == "mailing_filling contact_telegram")
        router.callback_query.register(self.save_mailing_callback, F.message.chat.type != "private", F.data == "mailing_filling_save")
        router.callback_query.register(self.change_mail_sending_delay_callback, F.message.chat.type != "private", F.data == "mailing_filling_change sending_delay")

    @group_chat_callback_decorator
    async def change_mail_author_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите автора письма"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_mailing_filling_keyboard())
        await state.set_state(MailingState.change_author)
    
    @group_chat_callback_decorator
    async def change_mail_topic_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nBведите тему письма"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_mailing_filling_keyboard())
        await state.set_state(MailingState.change_topic)
    
    @group_chat_callback_decorator
    async def change_mail_body_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите тело письма"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_mailing_filling_keyboard())
        await state.set_state(MailingState.change_body)
    
    @group_chat_callback_decorator
    async def change_mail_recipients_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите получателей письма"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_mailing_filling_keyboard())
        await state.set_state(MailingState.change_recipients)

    @group_chat_callback_decorator
    async def change_mail_sending_delay_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите задержку перед отправкой в минутах"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_mailing_filling_keyboard())
        await state.set_state(MailingState.change_send_delay)
    
    @group_chat_callback_decorator    
    async def change_mail_attachment_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nДобавьте файлы"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_mailing_filling_keyboard())
        await state.set_state(MailingState.change_attachment)
    
    @group_chat_callback_decorator
    async def change_mail_contact_type_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\n Укажите способ отправки письма"
        bot_message = await callback.message.edit_text(bot_message_text, reply_markup=get_mailing_filling_contact_type_keyboard())
        await state.set_state(MailingState.change_contact_type)
    
    @group_chat_callback_decorator
    async def set_telegram_contact_type_callback(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        mail_data = data.get("mail")
        mail_entity = mail_data.get("entity")
        mail_entity.contact_type = "telegram"
        bot_message = callback.message
        await state.update_data({"mail": {"entity": mail_entity, "message": bot_message}})
        response = await self.mailing_service.get_telegram_message(state)
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)
    
    @group_chat_callback_decorator
    async def set_email_contact_type_callback(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        mail_data = data.get("mail")
        mail_entity = mail_data.get("entity")
        mail_entity.contact_type = "email"
        bot_message = callback.message
        await state.update_data({"mail": {"entity": mail_entity, "message": bot_message}})
        response = await self.mailing_service.get_telegram_message(state)
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)
    
    @group_chat_callback_decorator 
    async def delete_mailing_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("Письмо удалено", reply_markup=get_go_to_main_menu_keyboard())
        await state.clear()

    @group_chat_callback_decorator
    async def save_mailing_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = "Письмо сохранено"
        await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_main_menu_keyboard())
        await self.mailing_service.save_mailing_message(state=state)

    @group_chat_callback_decorator
    async def go_back_to_filling_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message = await self.mailing_service.get_telegram_message(state)
        await state.set_state(MailingState.empty)
        await callback.message.edit_text(text=bot_message.get("message"), reply_markup=bot_message.get("keyboard"))
        
    @audio_to_text_converter
    async def change_mail_author_state(self, message: types.Message, state: FSMContext):
        response = await self.mailing_service.change_mail_author(message, state)
        data = await state.get_data()
        mailing_message_data = data.get("mail")
        bot_message: types.Message = mailing_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)

    @audio_to_text_converter
    async def change_mail_topic_state(self, message: types.Message, state: FSMContext):
        response = await self.mailing_service.change_mail_topic(message, state)
        data = await state.get_data()
        mailing_message_data = data.get("mail")
        bot_message: types.Message = mailing_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)

    @audio_to_text_converter
    async def change_mail_body_state(self, message: types.Message, state: FSMContext):
        response = await self.mailing_service.change_mail_body(message, state)
        data = await state.get_data()
        mailing_message_data = data.get("mail")
        bot_message: types.Message = mailing_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)

    @audio_to_text_converter
    async def change_mail_recipients_state(self, message: types.Message, state: FSMContext):
        response = await self.mailing_service.change_mail_recipients(message, state)
        data = await state.get_data()
        mailing_message_data = data.get("mail")
        bot_message: types.Message = mailing_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)

    async def change_mail_attachment_state(self, message: types.Message, state: FSMContext):
        response = await self.mailing_service.change_mail_attachment(message, state)
        data = await state.get_data()
        mailing_message_data = data.get("mail")
        bot_message: types.Message = mailing_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)

    @audio_to_text_converter
    async def change_mail_sending_delay_state(self, message: types.Message, state: FSMContext):
        response = await self.mailing_service.change_mail_sending_delay(message, state)
        data = await state.get_data()
        mailing_message_data = data.get("mail")
        bot_message: types.Message = mailing_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MailingState.empty)

