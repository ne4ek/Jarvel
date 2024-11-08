from abc import ABC, abstractmethod
from domain.entities.user import User
from domain.entities.user_chat import UserChat


class UserChatsRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int):
        pass

    @abstractmethod
    def get_user_id_by_company_code(self, company_code: str):
        pass

    @abstractmethod
    def get_companies_codes_by_user_id(self, user_id: int):
        pass

    @abstractmethod
    def save_user_chat(self, user_chat: UserChat):
        pass

    @abstractmethod
    def is_user_chat_exists(self, user_chat: UserChat):
        pass

