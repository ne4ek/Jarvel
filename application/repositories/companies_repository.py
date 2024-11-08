from abc import ABC, abstractmethod
from typing import List

from domain.entities.company import Company
from domain.entities.group_chat import GroupChat
from domain.entities.user import User


class CompaniesRepository(ABC):
    """
    Company repository abstract class.
    """

    @abstractmethod
    def save(self, company: Company):
        pass

    @abstractmethod
    def get_company_code_by_chat_id(self, chat_id: int):
        pass

    @abstractmethod
    def get_users_by_company_code(self, company_code: str) -> List[User]:
        pass

    @abstractmethod
    def get_owner_id_by_company_code(self, company_code: str):
        pass

    @abstractmethod
    def get_codes(self):
        pass

    @abstractmethod
    def is_company_code_exists(self, company_code: str):
        pass

    @abstractmethod
    def get_code_and_owner_id(self):
        pass
    
    @abstractmethod
    def add_user_id_by_company_code(self, user_id: int, company_code: str, role=str):
        pass

    @abstractmethod
    def get_name_by_company_code(self, company_code: str):
        pass

    @abstractmethod
    def get_names_by_user_id(self, user_id: int):
        pass

    @abstractmethod
    def get_names_by_owner_id(self, owner_id: int):
        pass

    @abstractmethod
    def get_description_by_company_code(self, company_code: str):
        pass

    @abstractmethod
    def is_group_registered_in_company(self, chat: GroupChat, conn=None, cursor=None) -> bool:
        pass
    
    @abstractmethod
    def add_group_chat_to_company(self, chat: GroupChat, conn=None, cursor=None):
        pass
    
    @abstractmethod
    def get_owner_by_company_code(self, company_code: str) -> User:
        pass
    
    @abstractmethod
    def is_user_registered_in_company(self, company_code: str, user_id: int) -> bool:
        pass