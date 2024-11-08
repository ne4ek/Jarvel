from abc import ABC, abstractmethod

from domain.entities.message import Message


class MessagesRepository(ABC):
    """
    Message repository abstract class.
    """

    @abstractmethod
    def save(self, message: Message):
        pass

    @abstractmethod
    def get_count_messages_by_chat_id(self, int):
        pass

    @abstractmethod
    def get_n_last_messages_by_chat_id(self, chat_id: int, bot_id: int, n: int):
        pass