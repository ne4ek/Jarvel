from .telegram_message_template import compose_telegram_task_filling_template
from domain.contracts.assistant import Assistant
from domain.entities.task import Task
from domain.entities.user import User
from application.providers.function_calls_provider import FunctionCallsProvider
from application.providers.prompts_provider import PromptsProvider
from application.repositories.companies_repository import CompaniesRepository
from application.telegram.handlers.group_chats.tasks.keyboards.compose_task_keyboard import get_menu_task_filling_keyboard
from application.tasks.validators.tasks_validators import TelegramTaskValidator
import json
from typing import Dict, List, Union
from openai import AsyncOpenAI
from fuzzywuzzy import fuzz
from datetime import datetime, time
from icecream import ic
import pytz

class TaskAssistant(Assistant):
    def __init__(self, api_key: str, model: str, temperature: int, initial_prompt: str, functions_provider: FunctionCallsProvider, company_repository: CompaniesRepository, change_data_prompts: PromptsProvider):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.temperature = temperature
        self.initial_prompt = {"role": "system", "content": initial_prompt}
        self.change_data_prompts = change_data_prompts
        self.functions_provider = functions_provider
        self.company_repository = company_repository

    async def get_all_parameters(self, messages: List[Dict], company_code: str) -> Dict:
        messages.insert(0, self.initial_prompt)
        messages.insert(1, self.__compose_prompt_with_dates())
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("extract_task_data"),
            function_call={"name": "extract_task_data"}
            
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        ic(extracted_data)
        return await self.__get_task_entity(extracted_data, company_code)
    
    async def change_task_author(self, messages: List[Dict], company_code: str) -> User:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_task_author})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_task_author"),
            function_call={"name": "change_task_author"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_author_name = extracted_data.get("task_author_name")
        new_author_user = await self.__get_mentioned_user(new_author_name, company_code)
        return new_author_user
    
    async def change_task_executor(self, messages: List[Dict], company_code: str) -> User:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_task_executor})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_task_executor"),
            function_call={"name": "change_task_executor"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_executor_name = extracted_data.get("task_executor_name")
        new_task_executor_user = await self.__get_mentioned_user(new_executor_name, company_code)
        return new_task_executor_user
    
    async def change_task_deadline(self, messages: List[Dict]) -> datetime:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_task_deadline})
        messages.insert(1,  self.__compose_prompt_with_dates())
        
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_task_deadline"),
            function_call={"name": "change_task_deadline"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        new_deadline_date = extracted_data.get("deadline_date")
        new_deadline_time = extracted_data.get("deadline_time")
        new_deadline_datetime = self.__convert_deadline_to_datetime(date_str=new_deadline_date,
                                                                    time_str=new_deadline_time)
        return new_deadline_datetime
    
    async def change_task_description(self, messages: List[Dict]) -> Dict:
        messages.insert(0, {"role": "system", "content": self.change_data_prompts.change_task_description})
        completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("change_task_description"),
            function_call={"name": "change_task_description"}
        )
        response_message = completion.choices[0].message
        extracted_data = json.loads(response_message.function_call.arguments)
        
        return extracted_data
    
    def compose_telegram_filling_message(self, task: Task, go_to_main_menu_button=True):
        # ic(task)
        message = compose_telegram_task_filling_template
        
        if task.author_user:
            author_name = task.author_user.full_name
            author_username = f"({task.author_user.username})"
        else:
            author_name = "Уточнить"
            author_username = ""
        if task.executor_user:
            executor_name = task.executor_user.full_name
            executor_username = f"({task.executor_user.username})"
        else:
            executor_name = "Уточнить"
            executor_username = ""
        deadline = task.deadline_datetime
        description = task.task
        tag = task.tag
        
        if not deadline:
            deadline = "Уточнить"
        else:
            deadline = deadline.strftime("%d.%m.%Y в %H:%M МСК")
        if not description:
            description = "Уточнить"
        if not tag:
            tag = "Уточнить"
        
        message = message.format(author_name,
                                 author_username,
                                 executor_name,
                                 executor_username,
                                 deadline,
                                 description,
                                 tag)
        
        return {"message": message, "keyboard": get_menu_task_filling_keyboard(TelegramTaskValidator.validate_all(task), go_to_main_menu=go_to_main_menu_button)}
    
    async def __get_task_entity(self, args: Dict, company_code: str) -> Task:
        task_author_name = args.get("task_author_name")
        task_author_user = await self.__get_mentioned_user(task_author_name, company_code)
        task_executor_name = args.get("executor_name")
        task_executor_user = await self.__get_mentioned_user(task_executor_name, company_code)
        deadline_date = args.get("deadline_date")
        deadline_time = args.get("deadline_time")
        deadline_datetime = self.__convert_deadline_to_datetime(deadline_date, deadline_time)
        task_description = args.get("task")
        task_summary = args.get("task_summary")
        tag = args.get("tag")
        
        task = Task()
        
        if isinstance(task_author_user, User):
            task.author_id = task_author_user.user_id
            task.author_user = task_author_user
        if isinstance(task_executor_user, User):
            task.executor_id = task_executor_user.user_id
            task.executor_user = task_executor_user
        task.deadline_datetime = deadline_datetime
        if task_description == "0":
            task_description = None
        task.task = task_description
        if task_summary == "0":
            task_summary = None
        task.task_summary = task_summary
        if tag == "0":
            tag = None
        task.tag = tag
        task.company_code = company_code
        
        return task
    
    def __convert_deadline_to_datetime(self, date_str: str, time_str: str):
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
            deadline_datetime = datetime.combine(date_datetime, time_datetime)
            ic(deadline_datetime)
            deadline_datetime = pytz.timezone('Europe/Moscow').localize(deadline_datetime)
            ic(deadline_datetime)
            return deadline_datetime
        elif date_datetime and not time_datetime:
            deadline_datetime = datetime.combine(date_datetime, time(23, 59, 59))
            deadline_datetime = pytz.timezone('Europe/Moscow').localize(deadline_datetime)
            return deadline_datetime
        elif time_datetime and not date_datetime:
            deadline_datetime = date_datetime.combine(datetime.now(), time_datetime)
            deadline_datetime = pytz.timezone('Europe/Moscow').localize(deadline_datetime)
            return deadline_datetime
        return None
    
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
    
    def __compose_prompt_with_dates(self):
        content = ""
        datetime_now = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        time_now = datetime_now.strftime("%H:%M")
        date_now = datetime_now.strftime("%d.%m.%Y")
        content += f"Дата сегодня: {date_now}\n"
        content += f"Время сейчас: {time_now}"
        return {"role": "system", "content": content}