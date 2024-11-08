from domain.contracts.assistant import Assistant
from domain.entities.mail import Mail


class TaskButtonClicked:
    def __init__(self, mailing_assistant: Assistant):
        self.mailing_assistant = mailing_assistant
    
    def execute(self):
        mail = Mail()
        return self.mailing_assistant.compose_telegram_filling_message(mail)
