from dataclasses import dataclass, field
from aiogram.types import User, Chat, Message, DateTime
from aiogram.client.bot import Bot
from typing import Optional

@dataclass
class TranscribedMessage:
    message_id: int
    chat: Chat
    text: str
    bot: Bot
    date: DateTime
    from_user: Optional[User] = field(default=None)
    reply_to_message: Optional[Message] = field(default=None)
    summarized_text: Optional[str] = field(default=None)
    original_message: Optional[Message] = field(default=None)
    
    async def reply(self, **kwargs):
        return await self.original_message.reply(**kwargs)
    
    async def answer(self, **kwargs):
        return await self.original_message.answer(**kwargs)
    
    async def delete(self, **kwargs):
        return await self.original_message.delete(**kwargs)