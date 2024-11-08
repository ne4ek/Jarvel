from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from domain.entities.company import Company
from domain.entities.meeting import Meeting
from application.repositories.companies_repository import CompaniesRepository

class CompaniesValidator(ABC):
    @staticmethod
    @abstractmethod
    def validate_name(name: str, company: Company = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_code(companies_repository: CompaniesRepository, code: str, company: Company = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_role(code: str, company: Company = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_description(description: str, company: Company = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_owner_id(owner_id: int, company: Company = None):
        pass

    @staticmethod
    @abstractmethod
    def validate_users_id(users_id: list[int], company: Company = None):
        pass

