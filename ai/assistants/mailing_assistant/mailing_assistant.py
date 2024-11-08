from .telegram_message_template import compose_telegram_mail_filling_template
from application.providers.function_calls_provider import FunctionCallsProvider
from application.telegram.handlers.group_chats.mailing.kayboards.compose_mailing_keyboard import get_menu_mailing_filling_keyboard
from application.providers.prompts_provider import PromptsProvider
from application.repositories.companies_repository import CompaniesRepository
from domain.entities.mail import Mail
from domain.entities.user import User
from domain.entities.unknown_user import UnknownUser
from domain.contracts.assistant import Assistant
from infrastructure.validators_impl.mail_validator import MailingValidatorImpl
from openai import AsyncOpenAI
from icecream import ic
from typing import Dict, List, Union
from fuzzywuzzy import fuzz
import json


class MailingAssistant(Assistant):
    def __init__(self, api_key: str, model: str, temperature: int, initial_prompt: str, functions_provider: FunctionCallsProvider, prompt_provider: PromptsProvider, company_repository: CompaniesRepository):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.temperature = temperature
        self.initial_prompt = {"role": "system", "content": initial_prompt}
        self.functions_provider = functions_provider
        self.change_data_prompts = prompt_provider
        self.company_repository = company_repository

    async def get_all_parameters(self, messages: List[Dict], company_code: str):
        messages.insert(0, self.initial_prompt)
        
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("extract_mail_data"),
            function_call={"name": "extract_mail_data"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        ic(extracted_data)
        return await self.__get_mail_entity(extracted_data, company_code)

    async def change_mail_author(self, messages: List[Dict], company_code: str) -> User:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_mail_author})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_mail_author"),
            function_call={"name": "change_mail_author"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_author_name = extracted_data.get("mail_author_name")
        new_author_user = self.__get_mentioned_user(new_author_name, company_code)
        return new_author_user
    
    async def change_mail_body(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_mail_body})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_mail_body"),
            function_call={"name": "change_mail_body"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_mail_body = extracted_data.get("mail_body")
        new_mail_topic = extracted_data.get("mail_topic")
        if new_mail_topic == "0":
            new_mail_topic = new_mail_body
        return {"mail_body": new_mail_body, "mail_topic": new_mail_topic}
    
    async def change_mail_topic(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_mail_topic})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_mail_topic"),
            function_call={"name": "change_mail_topic"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_mail_topic = extracted_data.get("mail_topic")
        return new_mail_topic

    async def change_mail_send_delay(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_mail_send_delay})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_mail_send_delay"),
            function_call={"name": "change_mail_send_delay"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_mail_send_delay = extracted_data.get("sending_delay")
        return new_mail_send_delay
    
    async def change_mail_recipients(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_mail_recipients})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_mail_recipients"),
            function_call={"name": "change_mail_recipients"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_mail_recipients = extracted_data.get("recipients")
        ic(new_mail_recipients)
        new_mail_sorted_recipients = await self.__sort_recipients(mentioned_users=new_mail_recipients,
                                                            company_code=company_code)
        return new_mail_sorted_recipients
    
    async def __get_mail_entity(self, args: Dict, company_code: str) -> Mail:
        mail_author_name: str = args.get("mail_author_name")
        mail_body: str = args.get("mail_body")
        mail_topic: str = args.get("mail_topic")
        recipients: List[Dict] = args.get("recipients")
        contact_type: str = args.get("contact_type")
        delay: int = args.get("sending_delay")
        
        mail = Mail()
        sorted_recipients = await self.__sort_recipients(mentioned_users=recipients, company_code=company_code)
        mail_author_user = await self.__get_mentioned_user(mentioned_user=mail_author_name, company_code=company_code)
        mail.recipients = sorted_recipients
        mail.author_user = mail_author_user
        ic(contact_type)
        if contact_type and contact_type != "no_assistant":
            mail.contact_type = contact_type
        else:
            mail.contact_type = "email"
        if delay:
            mail.send_delay = delay
        else:
            mail.send_delay = 1
        mail.body = mail_body
        mail.topic = mail_topic
        mail.company_code = company_code
        ic("__get_mail_entity", mail)
        return mail
    
    async def __sort_recipients(self, mentioned_users: List[Dict], company_code: str) -> Dict[str, List[User]]:
        users = {"known_recipients": [], "unknown_recipients": []}
        if not mentioned_users:
            return
        
        all_company_users = await self.company_repository.get_users_by_company_code(company_code)
        
        for mentioned_user in mentioned_users:
            if mentioned_user["name"] == "0":
                unknown_user = UnknownUser()
                if mentioned_user["email"] != "0":
                    unknown_user.email = mentioned_user["email"]
                if mentioned_user["telegram"] != "0":
                    unknown_user.username = mentioned_user["telegram"]
                users["unknown_recipients"].append(unknown_user)
                continue
            similiar_users = {}
            for company_user in all_company_users:
                ratio = fuzz.WRatio(mentioned_user["name"], company_user.full_name)
                if ratio == 100:
                    similiar_users[100] = [company_user]
                    break
                elif ratio >= 70:
                    if ratio not in similiar_users.keys():
                        similiar_users[ratio] = []
                    similiar_users[ratio].append(company_user)
            if 100 in similiar_users.keys():
                users["known_recipients"].append(similiar_users[100][0])
                continue
            if len(similiar_users.values()) != 0:
                ratio = max(similiar_users.keys())
                users["known_recipients"].append(similiar_users[ratio][0])
            else:
                unknown_user = UnknownUser(full_name=mentioned_user["name"])
                if mentioned_user["email"] != "0":
                    unknown_user.email = mentioned_user["email"]
                if mentioned_user["telegram"] != "0":
                    unknown_user.username = mentioned_user["telegram"]
                
                users["unknown_recipients"].append(unknown_user)
        return users

    async def __get_mentioned_user(self, mentioned_user: str, company_code: str) -> Union[User, None]:
        if mentioned_user == "0":
            return None
        all_company_users = await self.company_repository.get_users_by_company_code(company_code)
        similiar_users = {}
        for company_user in all_company_users:
            ratio = fuzz.WRatio(mentioned_user, company_user.full_name)
            if ratio == 100:
                return company_user
            elif ratio >= 70:
                if ratio not in similiar_users.keys():
                    similiar_users[ratio] = []
                similiar_users[ratio].append(company_user)
        try:
            ratio = max(similiar_users.keys())
            return similiar_users[ratio][0]
        except:
            return None
    
    def compose_telegram_filling_message(self, mail: Mail, go_to_main_menu_button=True):
        ic(mail)
        message = compose_telegram_mail_filling_template
        
        author = mail.author_user
        recipients = mail.recipients

        known_recipients = ""
        unknown_recipients = ""
        if recipients:
            for known_recipient in recipients.get("known_recipients"):
                if mail.contact_type == "telegram":
                    known_recipients += f"{known_recipient.full_name} ({known_recipient.username})\n"
                elif mail.contact_type == "email":
                    known_recipients += f"{known_recipient.full_name} ({known_recipient.email})\n"
            if recipients.get("unknown_recipients"):
                unknown_recipients = "❓ Неизвестные получатели:\n"
                for unknown_recipient in recipients.get("unknown_recipients"):
                    unknown_user_name = ""
                    unknown_user_username = ""
                    unknown_user_email = ""
                    if unknown_recipient.full_name:
                        unknown_user_name = unknown_recipient.full_name
                    if unknown_recipient.username:
                        unknown_user_username = f"({unknown_recipient.username})"
                    if unknown_recipient.email:
                        unknown_user_email = f"({unknown_recipient.email})"
                    if unknown_user_email or unknown_user_username:
                        unknown_recipients += f"{unknown_user_name}{unknown_user_username}{unknown_user_email}\n"
                    elif unknown_user_name:
                        unknown_recipients += f"{unknown_user_name}\n"
        else:
            known_recipients = "Уточнить"
        if mail.body not in  ["0", None]:
            body = mail.body
        else:
            body = "Уточнить"
        if mail.topic not in  ["0", None]:
            topic = mail.topic
        else:
            topic = "Уточнить"
        if author:
            if mail.contact_type == "telegram":
                author = f"{author.full_name} ({author.username})"
            elif mail.contact_type == "email":
                author = f"{author.full_name} ({author.email})"
        else:
            author = "Уточнить"
        if mail.send_delay and mail.send_delay != 0:
            delay = f"{mail.send_delay} мин."
        elif mail.send_delay == 0:
            delay = "моментально"
        else:
            delay = "Уточнить"
        message = message.format(author, known_recipients, unknown_recipients, topic, body, mail.contact_type, delay)
        return {"message": message, "keyboard": get_menu_mailing_filling_keyboard(MailingValidatorImpl.validate_created_mail(mail), go_to_main_menu=go_to_main_menu_button)}