from dataclasses import dataclass
from aiogram.types import User, Chat, Message, DateTime
from aiogram.client.bot import Bot


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
    from_user: User = None
    """*Optional*. Sender of the message; empty for messages sent to channels. For backward compatibility, the field contains a fake sender user in non-channel chats, if the message was sent on behalf of a chat."""
    reply_to_message: Message = None
    """*Optional*. For replies in the same chat and message thread, the original message. Note that the Message object in this field will not contain further *reply_to_message* fields even if it itself is a reply."""
    summarized_text: str = None
    """*Optional*. Summarized version of trancribed text"""
