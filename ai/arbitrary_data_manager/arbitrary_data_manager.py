from application.providers.function_calls_provider import FunctionCallsProvider
from application.providers.repositories_provider import RepositoriesDependencyProvider
from openai import AsyncOpenAI
import json
from icecream import ic
from typing import Union
from domain.entities.user import User
from fuzzywuzzy import fuzz

class ArbitraryDataManager:
    def __init__(self, api_key: str, model: str, temperature: int,
                 get_action_prompt: str, get_name_prompt: str,
                 get_user_data_prompt: str, update_user_data_prompt: str,
                 functions_provider: FunctionCallsProvider, repositories_proivider: RepositoriesDependencyProvider):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.temperature = temperature
        self.get_action_prompt = get_action_prompt
        self.get_name_prompt = get_name_prompt
        self.get_user_data_prompt = get_user_data_prompt
        self.update_user_data_prompt = update_user_data_prompt
        self.functions_provider = functions_provider
        self.arbitrary_data_repository = repositories_proivider.get_arbitrary_data_repository()
        self.user_repository = repositories_proivider.get_users_repository()
    
    
    async def execute_action(self, initial_messages: list, user_id: int):
        messages = [{"role": "system", "content": self.get_action_prompt}] + initial_messages
        ic(self.client)
        get_action_response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("arbitrary_data_action"),
            function_call={"name": "arbitrary_data_action"}
        )
        message = get_action_response.choices[0].message
        action = json.loads(message.function_call.arguments).get("action")
        
        action_to_func = {"GET": self.get_arbitrary_data,
                          "UPDATE": self.update_arbitrary_data}
        func = action_to_func.get(action)
        return await func(initial_messages, user_id)
    
    async def update_arbitrary_data(self, initial_messages: list, user_id: int):
        user_arbitrary_data: str = await self.arbitrary_data_repository.get_arbitrary_user_data(user_id)
        messages = [{"role": "system", "content": self.update_user_data_prompt}, {"role": "system", "content": user_arbitrary_data},] + initial_messages
        response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("update_action_function"),
            function_call={"name": "update_arbitrary_data"}
        )
        message = response.choices[0].message
        arguments: dict = json.loads(message.function_call.arguments)
        data = arguments.get("data")
        user_arbitrary_data: dict = json.loads(user_arbitrary_data)
        new_data = []
        updated_data = []
        for pair in data:
            key = pair["key"]
            value = pair["value"]
            if key in user_arbitrary_data:
                updated_data.append({key: value})
            else:
                new_data.append({key: value})
            user_arbitrary_data[key] = value
        user_arbitrary_data = json.dumps(user_arbitrary_data, ensure_ascii=False)
        await self.arbitrary_data_repository.set_arbitrary_user_data(user_id, user_arbitrary_data)

        return self.__compose_update_message(new_data, updated_data)
    
    async def get_arbitrary_data(self, inital_messages: list, user_id: int):
        messages = [{"role": "system", "content": self.get_name_prompt}]
        messages.extend(inital_messages)
        ic(messages)
        get_name_response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("get_action_functions"),
            function_call={"name": "get_name"}
        )
        message = get_name_response.choices[0].message
        name = json.loads(message.function_call.arguments).get("name")
        user_arbitrary_data = await self.__get_mentioned_user_arbitrary_data(name)
        ic(user_arbitrary_data)
        if not user_arbitrary_data:
            return {"message": "По вашему запросу совпадений не найдено!", "keyboard": None}
        messages = [{"role": "system", "content": self.get_user_data_prompt},
                    {"role": "system", "content": json.dumps(user_arbitrary_data).encode().decode('unicode-escape')}]
        messages.extend(inital_messages)
        ic(messages)
        response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions_provider.get_function_call("get_action_functions"),
            function_call={"name": "get_user_arbitrary_data"}
        )
        message = response.choices[0].message
        arguments: dict = json.loads(message.function_call.arguments)
        extracted_data = arguments.get("data")
        ic(extracted_data)
        return self.__compose_get_message(extracted_data)
    
    async def __get_mentioned_user_arbitrary_data(self, mentioned_user: str) -> Union[User, None]:
        all_users = await self.user_repository.get_all_users()
        similiar_users = {}
        for user in all_users:
            ratio = fuzz.WRatio(mentioned_user, user.full_name)
            if ratio == 100:
                ic(user.arbitrary_data)
                ic(user)
                return user.arbitrary_data
            elif ratio >= 70:
                if ratio not in similiar_users.keys():
                    similiar_users[ratio] = []
                similiar_users[ratio].append(user)
        try:
            ic(similiar_users)
            ratio = max(similiar_users.keys())
            return similiar_users[ratio][0].arbitrary_data
        except:
            return None
    
    def __compose_update_message(self, new_data: list, updated_data: list):
        telegram_message = \
'''
Обновление данных прошло успешно!
{}{}
'''
        new_data_message, updated_data_message = "", ""
        if new_data:
            new_data_message = "\nДобавленные данные:\n"
            for pair in new_data:
                for key, value in pair.items():
                    new_data_message += f"{key}: {value}\n"
        if updated_data:
            updated_data_message = "\nОбновленные данные:\n"
            for pair in updated_data:
                for key, value in pair.items():
                    updated_data_message += f"{key}: {value}\n"
        telegram_message = telegram_message.format(new_data_message, updated_data_message).strip()
        return {"message": telegram_message, "keyboard": None}
    
    def __compose_get_message(self, data: dict):
        telegram_message = \
"""
Вот данные, которые мне удалось найти:
{}
"""     
        list_of_data = ""
        for pair in data:
                if pair["key"] not in  ["0", 0, None] and pair["value"] not in ["0", 0, None]:
                    list_of_data += f"{pair['key']}: {pair['value']}\n"
        if not list_of_data:
            return {"message": "По вашему запросу данных не найдено!", "keyboard": None}
        telegram_message = telegram_message.format(list_of_data)
        return {"message": telegram_message, "keyboard": None}
#
# П (Василиса Пригожина): Мои любимые цветы - ромашки
# {"user_name": "Василиса Пригожина", "key": "favourite_flowers", "value": "Ромашки"}