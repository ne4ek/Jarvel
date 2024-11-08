from application.providers.usecases_provider import UseCasesProvider
from domain.entities.user import User
from typing import Union

class RegistrationService:
    def __init__(self, usecases: UseCasesProvider):
        self.usecases = usecases
    
    async def is_user_registered(self, user_id: int) -> bool:
        return await self.usecases.check_user_registration.execute(user_id)
    
    def is_email_valid(self, email: str) -> bool:
        return self.usecases.validate_email.execute(email)
    
    async def save_user(self, user_data: Union[dict, User]):
        if isinstance(user_data, dict):
            user = User()
            
            user.user_id = user_data.get("user_id")
            user.username = "@" + user_data.get("username")
            
            user_firstname = user_data.get("firstname")
            user_lastname = user_data.get("lastname")
            
            user.full_name = user_firstname + " " + user_lastname
            user.first_name = user_firstname
            user.last_name = user_lastname
            user.email = user_data.get("email")
            await self.usecases.save_user.execute(user)