from aiogram import Bot
from domain.entities.ctrl_message import CtrlMessage
from random import choice
from icecream import ic

class SendCtrlUseCase:
    def __init__(self, bot: Bot):
        self.bot = bot
        
    async def execute(self, ctrl_message: CtrlMessage):
        phrases = ["Какой статус?", "Какой статус у задачи?", "Как дела с этим?", "Как дела?", "Апаю"]
        text = ctrl_message.ctrl_usernames + " CTRL" + "\n" + f"{ctrl_message.fyi_usernames} FYI" + "\n\n" + choice(phrases)
        await self.bot.send_message(chat_id=ctrl_message.chat_id,
                                    text=text,
                                    reply_to_message_id=ctrl_message.reply_message_id)