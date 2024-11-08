from domain.contracts.assistant import Assistant
from domain.entities.meeting import Meeting
from aiogram import types

class TaskButtonClicked:
    def __init__(self, meeting_assistant: Assistant):
        self.meeting_assistant = meeting_assistant
    
    def execute(self):
        meeting = Meeting()
        return self.meeting_assistant.compose_telegram_filling_message(meeting)
