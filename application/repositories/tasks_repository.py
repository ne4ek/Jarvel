from abc import ABC, abstractmethod
from domain.entities.task import Task
from typing import List, Union
from datetime import datetime

class TasksRepository(ABC):
    """
    Abstract base class for task repositories.

    This class defines the interface for interacting with task data storage.

    Methods:
    - save(task: Task) -> None: Saves a task to the data storage.
    - get_all() -> List[Task]: Retrieves all tasks from the data storage.
    - get_by_company(company_code) -> List[Task]: Retrieves tasks by company code from the data storage.
    - get_by_executor(executor_id) -> List[Task]: Retrieves tasks by executor ID from the data storage.
    - get_by_author(author_id) -> List[Task]: Retrieves tasks by author ID from the data storage.
    - get_archived(user_id, company_code) -> List[Task]: Retrieves archived tasks by user ID and company code from the data storage.
    """
    @abstractmethod
    def save(self, task: Task) -> int:
        pass
    
    @abstractmethod
    def get_by_task_id(self, task_id: int) -> Task:
        pass
    
    @abstractmethod
    def get_all(self) -> List[Task]:
        pass
    
    @abstractmethod
    def get_by_company(self, company_code) -> List[Task]:
        pass
    
    @abstractmethod
    def get_by_executor(self, executor_id, company_code,) -> List[Task]:
        pass
    
    @abstractmethod
    def get_by_author(self, author_id, company_code,) -> List[Task]:
        pass

    @abstractmethod
    def get_personal_tasks(self, user_id: int, company_code: str) -> List[Task]:
        pass
    
    @abstractmethod
    def get_archived_author(self, author_id, company_code) -> List[Task]:
        pass

    @abstractmethod
    def get_archived_executor(self, executor_id, company_code) -> List[Task]:
        pass
    
    @abstractmethod
    def get_archived_personal_tasks(self, user_id: int, company_code: str) -> List[Task]:
        pass

    @abstractmethod
    def delete(self, task_id) -> List[Task]:
        pass

    @abstractmethod
    def set_status(self, task_id: int, status: str):
        pass
    
    @abstractmethod
    def set_description(self, task_id: int, new_description: str, new_task_summary: str = None, new_task_tag: str = None):
        pass
    
    @abstractmethod
    def set_deadline(self, task_id, deadline_datetime: datetime):
        pass
    
    @abstractmethod
    def set_tag(self, task_id, new_task_tag: str):
        pass

