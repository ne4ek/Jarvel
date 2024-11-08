import json
from datetime import datetime, timedelta
import pytz
from application.mailing.services.mail_scheduler_job_service import MailingJobService
from application.providers.repositories_provider import RepositoriesDependencyProvider
from aiogram import types
from aiogram.fsm.context import FSMContext
from domain.contracts.assistant import Assistant
from domain.entities.transcribed_message import TranscribedMessage
from domain.entities.mail import Mail
from typing import Union
from icecream import ic
from domain.entities.unknown_user import UnknownUser

class TelegramComposeMailService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider,
                 mailing_assistant: Assistant, mail_job_service: MailingJobService):
        self.mailing_assistant = mailing_assistant
        self.company_repository = repository_provider.get_companies_repository()
        self.user_repository = repository_provider.get_users_repository()
        self.mail_job_service = mail_job_service
        self.mail_repository = repository_provider.get_mailing_repository()


    async def change_mail_author(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        mail: Mail = data.get("mail").get("entity")
        bot_message = data.get("mail").get("message")
        mail_author_user = mail.author_user
        mail_author_name = mail_author_user.full_name

        messages = [
            {"role": "system", "content": f"mail_author_name: {mail_author_name}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_mail_author_user = await self.mailing_assistant.change_mail_author(messages,
                                                                               company_code)
        mail.author_user = new_mail_author_user
        await state.update_data({"mail": {"entity": mail, "message": bot_message}})
        telegram_message = await self.get_telegram_message(state)
        return telegram_message

    async def change_mail_topic(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        mail: Mail = data.get("mail").get("entity")
        bot_message = data.get("mail").get("message")
        mail_body = mail.body
        mail_topic = mail.topic

        messages = [
            {"role": "system", "content": f"mail_body: {mail_body}, mail_topic: {mail_topic}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_mail_topic = await self.mailing_assistant.change_mail_topic(messages,
                                                                        company_code)
        mail.topic = new_mail_topic
        await state.update_data({"mail": {"entity": mail, "message": bot_message}})
        telegram_message = await self.get_telegram_message(state)
        return telegram_message

    async def change_mail_body(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        mail: Mail = data.get("mail").get("entity")
        bot_message = data.get("mail").get("message")
        mail_body = mail.body
        mail_topic = mail.topic

        messages = [
            {"role": "system", "content": f"mail_body: {mail_body}, mail_topic: {mail_topic}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_mail_topic_and_body = await self.mailing_assistant.change_mail_body(messages, company_code)

        mail.topic = new_mail_topic_and_body.get("mail_topic")
        mail.body = new_mail_topic_and_body.get("mail_body")

        await state.update_data({"mail": {"entity": mail, "message": bot_message}})
        telegram_message = await self.get_telegram_message(state)

        return telegram_message

    async def change_mail_recipients(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        mail: Mail = data.get("mail").get("entity")
        bot_message = data.get("mail").get("message")
        recipients = mail.recipients
        recipients_list = []
        contact_type = mail.contact_type
        recipients_str = "No recipients"
        if recipients:
            for recipient in recipients.get("known_recipients"):
                recipient_str = recipient.full_name
                if contact_type == "telegram":
                    recipient_str += f" ({recipient.username})"
                elif contact_type == "email":
                    recipient_str += f" ({recipient.email})"
                recipients_list.append(recipient_str)
            for recipient in recipients.get("unknown_recipients"):
                recipient_str = ""
                if recipient.full_name:
                    recipient_str += recipient.full_name
                if recipient.email:
                    recipient_str += f" ({recipient.email})"
                if recipient.username:
                    recipient_str += f" ({recipient.username})"
                recipients_list.append(recipient_str)
            recipients_str = f"recipients: {recipients_list}"
        messages = [
            {"role": "system", "content": recipients_str},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_recipients = await self.mailing_assistant.change_mail_recipients(messages,
                                                                             company_code)
        mail.recipients = new_recipients
        await state.update_data({"mail": {"entity": mail, "message": bot_message}})
        telegram_message = await self.get_telegram_message(state)
        return telegram_message

    async def change_mail_sending_delay(self, message: types.Message, state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        mail: Mail = data.get("mail").get("entity")
        bot_message = data.get("mail").get("message")
        mail_send_delay = mail.send_delay
        messages = [
            {"role": "system", "content": f"mail_send_delay: {mail_send_delay}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_mail_send_delay = await self.mailing_assistant.change_mail_send_delay(messages, company_code)
        mail.send_delay = new_mail_send_delay
        await state.update_data({"mail": {"entity": mail, "message": bot_message}})
        telegram_message = await self.get_telegram_message(state)
        return telegram_message

    async def change_mail_attachment(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        mail_data = data.get("mail")
        mail_entity = mail_data.get("entity")
        bot_message = mail_data.get("message")
        mail_entity.attachment = message
        await state.update_data({"mail": {"entity": mail_entity, "message": bot_message}})
        telegram_message = await self.get_telegram_message(state)
        return telegram_message

    async def save_mailing_message(self, state: FSMContext):
        data = await state.get_data()
        mail: Mail = data.get("mail").get("entity")
        mail.author_id = mail.author_user.user_id
        mail.recipients_ids = [user.user_id for user in mail.recipients.get("known_recipients")]
        mail.unknown_recipients_data = [self.__unknown_user_to_json(unknown_user) for unknown_user in mail.recipients.get("unknown_recipients")]
        await self.mail_job_service.add_saved_mail_jobs(mail)
        await state.clear()

        # обработать= сохранить в БД (заполнить в бд)
        # save repository
        # достать способ отправки
        # если по тг = получатели идпользователей/ Неизвестным нельзя отправить
        # #если по емайл нет ид =
        # записываем почту в бд/ если нет адреса почты, то ничего не отправляем
        # пока просто отправить
        # достать адрес почты

    def __unknown_user_to_json(self, unknown_user: UnknownUser):
        return json.dumps(unknown_user.__dict__)

    async def get_telegram_message(self, state: FSMContext):
        data = await state.get_data()
        mail = data.get("mail").get("entity")
        return self.mailing_assistant.compose_telegram_filling_message(mail)

    async def __get_company_code(self, chat_id: int):
        return await self.company_repository.get_company_code_by_chat_id(chat_id)

    async def __get_message_sender_full_name(self, user_id: int):
        return await self.user_repository.get_full_name_by_id(user_id=user_id)
