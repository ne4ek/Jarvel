from abc import ABC, abstractmethod

from domain.entities.group_chat import GroupChat


class GroupChatsRepository(ABC):
    """
    Meeting repository abstract class.
    """

    @abstractmethod
    def get_company_code(self, chat_id: int):
        pass

    @abstractmethod
    def get_all_chat_ids(self):
        pass
    
    @abstractmethod
    def get_by_chat_id(self, chat_id: int) -> GroupChat:
        pass

    @abstractmethod
    def save_group_chat(self, group_chat: GroupChat):
        pass

    @abstractmethod
    def is_group_chat_exists(self, group_chat: GroupChat):
        pass

    @abstractmethod
    def get_name_by_chat_id(self, chat_id: int):
        pass

    @abstractmethod
    def delete(self, chat_id: int):
        pass

    @abstractmethod
    def is_chat_id_exists(self, chat_id: int):
        pass
    
    @abstractmethod
    def is_group_chat_assigned_to_company(self, chat_id: int) -> bool:
        pass