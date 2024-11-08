from openai import AsyncOpenAI
from typing import List, Dict
from domain.contracts.talker import Talker
from icecream import ic

class OfflineTalker(Talker):
    def __init__(self, api_key: str, model: str, temperature: int, prompt: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.prompt = prompt
    
    async def get_response(self, messages: List[Dict[str, str]]):
        messages.insert(-1, {"role": "system", "content": self.prompt})
        del messages[0]
        # ic(messages)
        response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature
        )
        ic(response)
        response = response.choices[0].message.content
        ic(response)        
        return response