from application.repositories.users_repository import UsersRepository
from domain.entities.user import User

class SaveUserUsecase:
    def __init__(self, user_repository: UsersRepository):
        self.user_repository = user_repository
        
    async def execute(self, user: User):
        await self.user_repository.save(user)