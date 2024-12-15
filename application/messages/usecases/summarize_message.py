from openai import AsyncOpenAI


class SummarizeMessage:
    def __init__(self, model: str, api_key: str, prompt: str, temperature: int):
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key)
        self.prompt = prompt
        self.temperature = temperature

    async def execute(self, text: str):
        pass