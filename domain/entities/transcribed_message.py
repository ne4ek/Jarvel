from dataclasses import dataclass, field
from aiogram.types import User, Chat, Message, DateTime
from aiogram.client.bot import Bot
from typing import Optional

@dataclass
class TranscribedMessage:
    message_id: int
    """Unique message identifier inside this chat"""
    chat: Chat
    """Chat the message belongs to"""
    text: str
    """Transcribed version of the original message"""
    bot: Bot
    """Bot instance"""
    date: DateTime
    """Date the message was sent in Unix time. It is always a positive number, representing a valid date."""
    from_user: Optional[User] = field(default=None)
    """*Optional*. Sender of the message; empty for messages sent to channels. For backward compatibility, the field contains a fake sender user in non-channel chats, if the message was sent on behalf of a chat."""
    reply_to_message: Optional[Message] = field(default=None)
    """*Optional*. For replies in the same chat and message thread, the original message. Note that the Message object in this field will not contain further *reply_to_message* fields even if it itself is a reply."""
    summarized_text: Optional[str] = field(default=None)
    """*Optional*. Summarized version of trancribed text"""
    original_message: Optional[Message] = field(default=None)
    """*Optional*. Original message object"""
    
    async def reply(self, **kwargs):
        return await self.original_message.reply(**kwargs)
    
    async def answer(self, **kwargs):
        return await self.original_message.answer(**kwargs)
    
    async def delete(self, **kwargs):
        return await self.original_message.delete(**kwargs)