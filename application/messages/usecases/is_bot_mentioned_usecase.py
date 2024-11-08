from typing import List
import re

class IsBotMentionedUseCase:
    def __init__(self, bot_mentions: List[str]):
        self.search_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(mention) for mention in bot_mentions) + r')\b', re.IGNORECASE)

    def execute(self, text: str) -> bool:
        
        return bool(self.search_pattern.search(text))