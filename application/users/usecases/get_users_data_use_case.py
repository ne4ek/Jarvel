from application.repositories.users_repository import UsersRepository
from domain.entities.user import User


class GetUsersDataUseCase:
    def __init__(self, users_repository: UsersRepository):
        self.users_repository = users_repository

    async def is_user_exists(self, user_id: int) -> User:
        content = await self.users_repository.is_user_exists(user_id=user_id)
        return content






