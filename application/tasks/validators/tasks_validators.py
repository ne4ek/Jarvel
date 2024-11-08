from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities.task import Task
from domain.entities.user import User
from icecream import ic
import pytz

class TaskValidator(ABC):
    @abstractmethod
    def validate_deadline(deadline) -> bool:
        pass
    
    @abstractmethod
    def validate_task(task) -> bool:
        pass


class TelegramTaskValidator(TaskValidator):
    @staticmethod
    def validate_all(task: Task):
        validation_deadline = TelegramTaskValidator.validate_deadline(task.deadline_datetime) 
        validation_user_ids = TelegramTaskValidator.validate_user_id(task.author_user) and TelegramTaskValidator.validate_user_id(task.executor_user)
        validation_task = TelegramTaskValidator.validate_task(task.task)
        ic(validation_deadline, validation_user_ids, validation_task)
        
        validation = validation_task and validation_deadline and validation_user_ids
        return validation
        
    @staticmethod
    def validate_deadline(deadline) -> bool:
        current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        if not isinstance(deadline, datetime):
            return False
        if deadline <= current_datetime:
            return False
        return True
    
    @staticmethod
    def validate_user_id(user) -> bool:
        if not isinstance(user, User):
            return False
        return True

    @staticmethod
    def validate_task(task) -> bool:
        if not isinstance(task, str) or len(task) < 1:
            return False
        return True