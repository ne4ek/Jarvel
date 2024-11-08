import re

class ValidateEmailUseCase:
    def __init__(self):
        self.email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    
    def execute(self, email: str):
        if self.email_regex.match(email):
            return True
        return False