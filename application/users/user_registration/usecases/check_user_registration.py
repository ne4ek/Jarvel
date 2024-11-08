from application.repositories.users_repository import UsersRepository

class CheckUserRegistrationUseCase:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_id: int):
        is_user_exists = await self.user_repository.is_user_exists(user_id)
        if not is_user_exists:
            return False
        return True
    