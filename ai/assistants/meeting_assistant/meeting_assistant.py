from application.providers.function_calls_provider import FunctionCallsProvider
from application.repositories.companies_repository import CompaniesRepository
from application.providers.prompts_provider import PromptsProvider
from application.telegram.handlers.group_chats.meetings.keyboards.compose_meeting_keyboard import get_menu_meeting_filling_keyboard
from domain.contracts.assistant import Assistant
from domain.entities.user import User
from domain.entities.meeting import Meeting
from domain.entities.unknown_user import UnknownUser
from .telegram_message_template import compose_telegram_meeting_filling_template
from infrastructure.config.validators_config import meeting_validator
from typing import Dict, List, Union
from openai import AsyncOpenAI
from fuzzywuzzy import fuzz
from datetime import timedelta, datetime
from icecream import ic
import pytz
import json


class MeetingAssistant(Assistant):
    def __init__(self, api_key: str, model: str, temperature: int, prompt: str, functions_provider: FunctionCallsProvider, company_repository: CompaniesRepository, change_data_prompts: PromptsProvider):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.temperature = temperature
        self.prompt = prompt
        self.functions_provider = functions_provider
        self.company_repository = company_repository
        self.change_data_prompts = change_data_prompts

    async def get_all_parameters(self, messages: List[Dict], company_code: str) -> Dict:
        args = {}
        dates_messages = messages.copy()
        dates_messages.insert(1, self.__get_datetime_prompt_now())
        dates = await self.client.chat.completions.create(
            messages=dates_messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("compose_all_meeting_dates"),
            function_call={"name": "compose_meeting_dates"}
            
        )
        participants = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("compose_all_meeting_participants"),
            function_call={"name": "compose_meeting_participants"}
            
        )
        extra_data = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("compose_all_meeting_extra_data"),
            function_call={"name": "compose_meeting_extra_data"}
            
        )
        response_message_1 = dates.choices[0].message
        response_message_2 = participants.choices[0].message
        response_message_3 = extra_data.choices[0].message
        meeting_dates = json.loads(response_message_1.function_call.arguments)
        meeting_participants = json.loads(response_message_2.function_call.arguments)
        meeting_extra_data = json.loads(response_message_3.function_call.arguments)
        
        args = dict(args,
                    **meeting_dates,
                    **meeting_participants,
                    **meeting_extra_data)
        ic(args)
        meeting_entity = await self.__get_meeting_entity(args, company_code)
        return meeting_entity
    
    async def change_meeting_topic(self, messages: List[Dict], company_code: str) -> str:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_meeting_topic})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_meeting_topic"),
            function_call={"name": "change_meeting_topic"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_meeting_name = extracted_data.get("topic")
        return new_meeting_name
    
    async def change_meeting_duration(self, messages: List[Dict], company_code: str) -> str:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_meeting_duration})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_meeting_duration"),
            function_call={"name": "change_meeting_duration"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_meeting_duration = extracted_data.get("duration")
        return new_meeting_duration
    
    async def change_meeting_remind_time(self, messages: List[Dict], company_code: str, meeting_datetime: datetime) -> timedelta:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_meeting_remind_datetime})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_meeting_remind_datetime"),
            function_call={"name": "change_meeting_remind_datetime"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_meeting_remind_datetime = self.__get_remind_datetime(time_str=extracted_data.get("remind_time"),
                                                                 date_str=extracted_data.get("remind_date"),
                                                                 meeting_datetime=meeting_datetime)
        return new_meeting_remind_datetime
    
    async def change_meeting_participants(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_meeting_participants})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_meeting_participants"),
            function_call={"name": "change_meeting_participants"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_participants_data = extracted_data.get("participants_data")
        invite_all = extracted_data.get("invite_all")
        new_sorted_participants = await self.__sort_participants(new_participants_data,
                                                           company_code)
        if invite_all == 1:
            all_company_users = await self.company_repository.get_users_by_company_code(company_code)
        else:
            all_company_users = []
        for company_user in all_company_users:
            if len(new_sorted_participants["known_participants"]):
                if company_user.user_id not in [user.user_id for user in new_sorted_participants["known_participants"]]:
                    new_sorted_participants["known_participants"].append(company_user)
            else:
                new_sorted_participants["known_participants"].append(company_user)
            
        return new_sorted_participants
    
    async def change_meeting_moderator(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_meeting_moderator})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_meeting_moderator"),
            function_call={"name": "change_meeting_moderator"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_meeting_moderator_name = extracted_data.get("moderator_name")
        new_meeting_moderator_user = await self.__get_mentioned_user(new_meeting_moderator_name,
                                                               company_code)
        return new_meeting_moderator_user

    async def change_meeting_datetime(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_meeting_datetime})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_meeting_datetime"),
            function_call={"name": "change_meeting_datetime"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_meeting_date = extracted_data.get("meeting_date")
        new_meeting_time = extracted_data.get("meeting_time")
        new_meeting_datetime = self.__get_meeting_datetime(new_meeting_date,
                                                           new_meeting_time)
        return new_meeting_datetime

    async def __get_meeting_entity(self, args: Dict, company_code: str) -> Meeting:
        meeting = Meeting()
        
        meeting_date = args.get("meeting_date") 
        meeting_time = args.get("meeting_time")
        meeting_datetime = self.__get_meeting_datetime(meeting_date,
                                                       meeting_time)
        if meeting_datetime:
            meeting.meeting_datetime = meeting_datetime
            remind_date = args.get("remind_date")
            remind_time = args.get("remind_time")
            
            if remind_date != "0" or remind_time != "0":
                remind_datetime = self.__get_remind_datetime(date_str=remind_date,
                                                         time_str=remind_time,
                                                         meeting_datetime=meeting_datetime)
            else:
                remind_datetime = meeting_datetime - timedelta(minutes=5)
            meeting.remind_datetime = remind_datetime
        
        author_name = args.get("author_name")
        author_user = await self.__get_mentioned_user(author_name, company_code)
        meeting.author_user = author_user
        if author_user:
            meeting.author_id = author_user.user_id
            
        moderator_name = args.get("moderator_name")
        moderator_user = await self.__get_mentioned_user(moderator_name, company_code)
        meeting.moderator_user = moderator_user
        if moderator_user:
            meeting.moderator_id = moderator_user.user_id
        
        meeting_invite_all = args.get("invite_all")
        if meeting_invite_all == 1:
            all_company_users = await self.company_repository.get_users_by_company_code(company_code)
        else:
            all_company_users = []
        participants_data = args.get("participants_data")
        sorted_participants = await self.__sort_participants(participants_data, company_code)
        for company_user in all_company_users:
            if len(sorted_participants["known_participants"]):
                if company_user.user_id not in [user.user_id for user in sorted_participants["known_participants"]]:
                    sorted_participants["known_participants"].append(company_user)
            else:
                sorted_participants["known_participants"].append(company_user)

        meeting.participants_users = sorted_participants if len(sorted_participants["known_participants"]) or len(sorted_participants["unknown_participants"]) else None
        
        meeting_link = args.get("link")
        if meeting_link == "0":
            meeting.link = None
        else:
            meeting.link = meeting_link
        
        meeting_topic = args.get("topic")
        if meeting_topic == "0":
            meeting.topic = None
        else:
            meeting.topic = meeting_topic
            
        meeting.invitation_type = args.get("invitation_type")
        
        meeting.duration = args.get("duration")
        
        meeting.company_code = company_code
        
        return meeting
        
        
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
    
    async def __sort_participants(self, mentioned_users: List[str], company_code) -> Dict[str, List[User]]:
        users = {"known_participants": [], "unknown_participants": []}
        if not mentioned_users:
            return users
        
        all_company_users = await self.company_repository.get_users_by_company_code(company_code)
        for mentioned_user in mentioned_users:
            if mentioned_user.get("name") and mentioned_user["name"] == "0":
                unknown_user = UnknownUser()
                if mentioned_user.get("email") and mentioned_user["email"] != "0":
                    unknown_user.email = mentioned_user["email"]
                if mentioned_user.get("telegram") and mentioned_user["telegram"] != "0":
                    unknown_user.username = mentioned_user["telegram"]
                users["unknown_participants"].append(unknown_user)
            similiar_users = {}
            for company_user in all_company_users:
                ratio = fuzz.WRatio(mentioned_user, company_user.full_name)
                if ratio == 100:
                    if ratio not in similiar_users:
                        similiar_users[ratio] = []
                    similiar_users[100].append(company_user)
                    break
                elif ratio >= 70:
                    if ratio not in similiar_users:
                        similiar_users[ratio] = []
                    similiar_users[ratio].append(company_user)
            if 100 in similiar_users.keys():
                ic(similiar_users)
                users["known_participants"].append(similiar_users[100][0])
                continue
            if len(similiar_users.values()) != 0:
                ratio = max(similiar_users.keys())
                users["known_participants"].append(similiar_users[ratio][0])
            else:
                unknown_user = UnknownUser()
                if mentioned_user.get("email") and mentioned_user["email"] != "0":
                    unknown_user.email = mentioned_user["email"]
                if mentioned_user.get("telegram") and mentioned_user["telegram"] != "0":
                    unknown_user.username = mentioned_user["telegram"]
                unknown_user.full_name = mentioned_user.get("name")
                users["unknown_participants"].append(unknown_user)
        return users
    
    
    def __get_meeting_datetime(self, date_str: str, time_str: str):
        date_datetime, time_datetime = None, None
        try:
            date_datetime = datetime.strptime(date_str, "%d.%m.%Y").date()
        except Exception as e:
            pass
        try:
            time_datetime = datetime.strptime(time_str, "%H:%M").time()
        except Exception as e:
            pass
        if date_datetime and time_datetime:
            meeting_datetime = datetime.combine(date_datetime, time_datetime)
            meeting_datetime = pytz.timezone('Europe/Moscow').localize(meeting_datetime)
            return meeting_datetime
        elif date_datetime:
            ic(date_datetime)
            date_datetime = pytz.timezone('Europe/Moscow').localize(datetime.combine(date_datetime, datetime.min.time()))
            return date_datetime
        elif time_datetime:
            date_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow')).date()
            meeting_datetime = datetime.combine(date_datetime, time_datetime)
            meeting_datetime = pytz.timezone('Europe/Moscow').localize(meeting_datetime)
            return meeting_datetime
        return None
    
    def __get_remind_datetime(self, date_str: str, time_str: str, meeting_datetime: datetime):
        date_datetime, time_datetime = None, None
        try:
            date_datetime = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError as e:
            pass
        try:
            time_datetime = datetime.strptime(time_str, "%H:%M").time()
        except ValueError as e:
            pass
        if date_datetime and time_datetime:
            remind_datetime = datetime.combine(date_datetime, time_datetime)
            remind_datetime = pytz.timezone('Europe/Moscow').localize(remind_datetime)
            return remind_datetime          
        elif time_datetime:
            remind_datetime = datetime.combine(meeting_datetime.date, time_datetime)
            remind_datetime = pytz.timezone('Europe/Moscow').localize(remind_datetime)
            return remind_datetime
        return None

    def __get_datetime_prompt_now(self):
        current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        return {"role": "system", "content": f"Дата на сегодня - {current_datetime.date()}\nВремя - {current_datetime.time()}"}

    def compose_telegram_filling_message(self, meeting: Meeting, go_to_main_menu_button=True):
        message = compose_telegram_meeting_filling_template
        
        if meeting.topic:
            topic = meeting.topic
        else:
            topic = "Уточнить"
            
        if meeting.meeting_datetime:
            meeting_datetime = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M МСК")
        else:
            meeting_datetime = "Уточнить"
            
        if meeting.remind_datetime and meeting.meeting_datetime and (meeting.meeting_datetime > meeting.remind_datetime):
            meeting_remind_datetime = meeting.remind_datetime.strftime("%d.%m.%Y в %H:%M МСК")
        else:
            if meeting.meeting_datetime:
                meeting_remind_datetime = meeting.meeting_datetime - timedelta(minutes=10)
                meeting_remind_datetime = meeting.meeting_datetime.strftime("%d.%m.%Y в %H:%M")
            else:
                meeting_remind_datetime = "Уточнить"
                
        if meeting.moderator_user:
            moderator_name = meeting.moderator_user.full_name
            moderator_username = f"({meeting.moderator_user.username})"
            moderator = f"{moderator_name} {moderator_username}"
        else:
            moderator = "Уточнить"
            
        known_participants = ""
        unknown_participants = ""
        invitation_type = meeting.invitation_type
        
        participants_users = meeting.participants_users
        
        if participants_users:
            for known_user in participants_users.get("known_participants"):
                if invitation_type == "telegram":
                    known_user_name = known_user.full_name
                    known_user_username = known_user.username
                    known_participants += f"{known_user_name} ({known_user_username})\n"
                elif invitation_type == "email":
                    known_user_name = known_user.full_name
                    known_user_email = known_user.email
                    known_participants += f"{known_user_name} ({known_user_email})\n"
            if participants_users.get("unknown_participants"):
                unknown_participants = "❓ Неизвестные участники:\n"
                for unknown_user in participants_users.get("unknown_participants"):
                    unknown_user_name = ""
                    unknown_user_username = ""
                    unknown_user_email = ""
                    ic(unknown_user)
                    if unknown_user.full_name:
                        unknown_user_name = unknown_user.full_name
        
                    if unknown_user.username:
                        unknown_user_username = f" ({unknown_user.username})"
                    if unknown_user.email:
                        unknown_user_email = f" ({unknown_user.email})"
                    ic(unknown_user_email, unknown_user_username, unknown_user_name)
                    if unknown_user_username or unknown_user_email:
                        unknown_participants += f"{unknown_user_name}{unknown_user_username}{unknown_user_email}\n"
                    elif unknown_user_name:
                        unknown_participants += f"{unknown_user_name}\n"
        else:
            known_participants = "Уточнить"
            unknown_participants = ""
        
        if meeting.link:
            link = meeting.link
        else:
            link = "Уточнить"
        
        if meeting.duration:
            duration = meeting.duration
        else:
            duration = "30"
        
        message = message.format(topic,
                                 meeting_datetime,
                                 meeting_remind_datetime,
                                 moderator,
                                 known_participants,
                                 unknown_participants,
                                 invitation_type,
                                 link,
                                 duration)
        
        return {"message": message, "keyboard": get_menu_meeting_filling_keyboard(meeting_validator.validate_created_meeting(meeting), go_to_main_menu=go_to_main_menu_button)}