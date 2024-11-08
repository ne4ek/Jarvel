# src/application/interfaces/telegram_sender_interface.py
from abc import ABC, abstractmethod

class TelegramSenderInterface(ABC):
    @abstractmethod
    async def send_message(self):
        pass
