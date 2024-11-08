from domain.entities.user import User
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from application.repositories.users_repository import UsersRepository
import json
from icecream import ic 

class PostgresUsersRepositoryAsync(UsersRepository):
    def __init__(self, db_connection_pool):
        self._connection_pool = db_connection_pool

    @staticmethod
    @open_and_close_connection
    async def get_by_id(user_id: int, connection=None) -> User:
        result = await connection.fetch(f"SELECT * FROM public.\"user\" WHERE user_id = {user_id}")
        if result:
            user_data = result[0]
            return User(user_id=user_data['user_id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        )
        return None

    @staticmethod
    @open_and_close_connection
    async def get_by_id_list(user_id_list: list[int], connection=None) -> list[User]:
        result = await connection.fetch(
            "SELECT user_id, username, first_name, last_name, email, personal_link, arbitrary_data FROM public.\"user\" WHERE user_id = ANY($1);", 
            user_id_list
        )
        return [User(user_id=user_data['user_id'],
                     username=user_data['username'],
                     email=user_data['email'],
                     personal_link=user_data['personal_link'],
                     first_name=user_data['first_name'],
                     last_name=user_data['last_name'],
                     ) for user_data in result]

    @staticmethod
    @open_and_close_connection
    async def get_full_name_by_id(user_id: int, connection=None) -> str:
        result = await connection.fetch(
            f"SELECT first_name || ' ' || last_name AS full_name FROM public.\"user\" WHERE user_id = {user_id};"
        )
        return result[0]['full_name'] if result else None

    @staticmethod
    @open_and_close_connection
    async def is_user_exists(user_id: int, connection=None) -> bool:
        result = await connection.fetch(
            "SELECT EXISTS(SELECT 1 FROM public.\"user\" WHERE user_id = $1)", 
            user_id
        )
        return result[0]['exists'] if result else False

    @staticmethod
    @open_and_close_connection
    async def get_username_by_id(user_id: int, connection=None) -> str:
        result = await connection.fetch(
            f"SELECT username FROM public.\"user\" WHERE user_id = {user_id}"
        )
        return result[0]['username'] if result else None

    @staticmethod
    @open_and_close_connection
    async def get_all_users(connection=None) -> list[User]:
        result = await connection.fetch("SELECT * FROM public.\"user\"")
        return [User(user_id=row['user_id'],
                     username=row['username'],
                     email=row['email'],
                     first_name=row['first_name'],
                     last_name=row['last_name'],
                     ) for row in result]

    @staticmethod
    @open_and_close_connection
    async def get_email_by_id(user_id: int, connection=None) -> str:
        result = await connection.fetch(
            f"SELECT email FROM public.\"user\" WHERE user_id = {user_id}"
        )
        return result[0]['email'] if result else None

    @staticmethod
    @open_and_close_connection
    async def get_name_by_id(user_id: int, connection=None) -> str:
        result = await connection.fetch(
            f"SELECT first_name || ' ' || last_name AS name FROM public.\"user\" WHERE user_id = {user_id}"
        )
        return result[0]['name'] if result else None

    @staticmethod
    @open_and_close_connection
    async def save(user: User, connection=None) -> None:
        await connection.fetch(
            "INSERT INTO public.\"user\" (user_id, username, first_name, last_name, email, arbitrary_data) VALUES ($1, $2, $3, $4, $5, $6::jsonb);",
            user.user_id,
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            user.arbitrary_data,
        )

    @staticmethod
    @open_and_close_connection
    async def update(user: User, connection=None) -> None:
        ic(user)

        await connection.fetch(
            "UPDATE public.\"user\" SET username = $1, first_name = $2, last_name = $3, email = $4, arbitrary_data = $5::jsonb WHERE user_id = $6",
            user.username, user.first_name, user.last_name, user.email, user.arbitrary_data, user.user_id
        )

    @staticmethod
    @open_and_close_connection
    async def save_personal_link(user_id: int, personal_link: str, connection=None) -> None:
        await connection.fetch(
            "UPDATE public.\"user\" SET personal_link = $1 WHERE user_id = $2",
            (personal_link, user_id)
        )

    @staticmethod
    @open_and_close_connection
    async def save_email(user_id: int, email: str, connection=None) -> None:
        await connection.fetch(
            "UPDATE public.\"user\" SET email = $1 WHERE user_id = $2",
            email, user_id
        )

    @staticmethod
    @open_and_close_connection
    async def is_user_registered_in_company(user_id: int, company_code: str, connection=None) -> bool:
        result = await connection.fetch(
            f"""
            SELECT EXISTS(
                SELECT 1 
                FROM public.user_company 
                JOIN public.company ON public.user_company.company_id = public.company.company_id 
                WHERE public.user_company.user_id = {user_id} 
                AND public.company.company_code = '{company_code}'
            )
            """
        )
        return result[0]['exists'] if result else False
