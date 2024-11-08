from domain.contracts.assistant import Assistant
from domain.entities.task import Task
from aiogram import types

class TaskButtonClicked:
    def __init__(self, task_assistant: Assistant):
        self.task_assistant = task_assistant
    
    def execute(self):
        task = Task()
        return self.task_assistant.compose_telegram_filling_message(task)
        