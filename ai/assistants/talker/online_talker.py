from openai import AsyncOpenAI
from typing import List, Dict
from aiogram import types
from domain.contracts.talker import Talker
from icecream import ic
from application.providers.repositories_provider import RepositoriesDependencyProvider
class OnlineTalker(Talker):
    def __init__(self, api_key: str, model: str, prompt: str, repositories_provider: RepositoriesDependencyProvider):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
        self.model = model
        self.prompt = prompt
        self.user_rep = repositories_provider.get_users_repository()
        
    async def get_response(self, message: types.Message):
        messages = [{"role": "system", "content": self.prompt}]
        ic(self.model)
        content = \
"""
message_id: {message_id}
user_name: {user_name}
message: {text}
"""
        if message.reply_to_message and message.reply_to_message.from_user.id == message.bot.id:
            messages[0]["content"] += "\n\nКонтекст на этот вопрос:\n" + content.format(message_id=message.reply_to_message.message_id,
                                                                                        user_name="Ассистент Ягодка",
                                                                                        text=message.reply_to_message.text)
        user_full_name = await self.user_rep.get_full_name_by_id(message.from_user.id)
        messages.append({"role": "user", "content": content.format(message_id=message.message_id,
                                                                   user_name=user_full_name if user_full_name else message.from_user.full_name,
                                                                   text=message.text)})
        ic(messages)
        response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model
        )
        response = response.choices[0].message.content
        return response