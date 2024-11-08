from application.providers.function_calls_provider import FunctionCallsProvider
from openai import AsyncOpenAI
from aiogram import types
from typing import List, Dict
from datetime import datetime
import pytz
import json
from icecream import ic
from .online_talker import OnlineTalker
from application.providers.repositories_provider import RepositoriesDependencyProvider


class Talker:
    def __init__(self, api_key: str, model: str, temperature: str, get_talker_type_prompt: str, functions_provider: FunctionCallsProvider, talker_types: dict):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.temperature = temperature
        self.get_talker_type_prompt = get_talker_type_prompt
        self.function_provider = functions_provider
        self.talker_types = talker_types
    
    async def get_response(self, messages: List[Dict[str, str]], user_message: types.Message):
        messages.insert(0, {"role": "system", "content": self.get_talker_type_prompt})
        datetime_prompt = self.__get_datetime_prompt_now()
        messages.insert(1, datetime_prompt)
        talker_type_function = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.function_provider.get_function_call("get_talker_type"),
            function_call={"name": "get_talker_type"}
        )
        response = talker_type_function.choices[0].message
        talker_type = json.loads(response.function_call.arguments).get("talker_type")
        talker_class = self.talker_types.get(talker_type)
        if isinstance(talker_class, OnlineTalker):
            ic("Online talker is called")
            response = await talker_class.get_response(user_message)
        else:
            ic("Offline talker is called")
            response = await talker_class.get_response(messages)
        if ("message_id:" in response or "user_name:" in response) and "message:" in response:
            response = response.split("message: ")[-1]
        return {"message": response, "keyboard": None}
    
    def __get_datetime_prompt_now(self):
        current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        return {"role": "system", "content": f"Дата на сегодня - {current_datetime.date()}\nВремя - {current_datetime.time()}"}