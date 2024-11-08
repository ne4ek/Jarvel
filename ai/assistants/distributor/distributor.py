from domain.contracts.assistant import Assistant
from typing import Dict, List
import json
from openai import AsyncOpenAI
from icecream import ic

class Distributor:
    def __init__(self, api_key: str, model: str, temperature: int, prompt: str, function: Dict):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.temperature = temperature
        self.prompt = {"role": "system", "content": prompt}
        self.functions = function
        self._available_assistants = {}

    def add_assistant(self, assistant: Dict[str, Dict[str, Assistant]]):
        for key, value in assistant.items():
            self._available_assistants[key] = value

    async def get_assistant(self, messages: List[Dict[str, str]]) -> Assistant:
        messages.insert(0, self.prompt)
        
        response = await self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            functions=self.functions,
            function_call={"name": "get_assistant"}
        )
        response_message = response.choices[0].message
        
        assistant_to_call = json.loads(response_message.function_call.arguments).get("assistant_name")
        if assistant_to_call == "no_assistant" or assistant_to_call is None:
            assistant_to_call = "talker"
        return self._available_assistants[assistant_to_call]