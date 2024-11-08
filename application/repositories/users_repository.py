from abc import ABC, abstractmethod
from domain.entities.user import User
from typing import List, Union

class UsersRepository(ABC):
    @abstractmethod
    def get_full_name_by_id(self, user_id: int) -> Union[str, None]:
        pass

    @abstractmethod
    def is_user_exists(self, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_username_by_id(self, user_id: int) -> str:
        pass

    @abstractmethod
    def get_by_id(self, user_id: int) -> User:
        pass
    
    @abstractmethod
    def get_by_id_list(user_id_list: list[int], conn=None, cursor=None) -> list[User]:
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        pass


    @abstractmethod
    def get_email_by_id(self, user_id: str):
        pass


    @abstractmethod
    def save(self, user: User):
        pass

    @abstractmethod
    def get_name_by_id(self, user_id: int):
        pass

    @abstractmethod
    def update(self, user: User):
        pass

    @abstractmethod
    def save_personal_link(self, user_id: int, personal_link: str):
        pass

    @abstractmethod
    def save_email(self, user_id: int, email: str):
        pass
    
    @abstractmethod
    def is_user_registered_in_company(self, user_id: int, company_code: str):
        pass