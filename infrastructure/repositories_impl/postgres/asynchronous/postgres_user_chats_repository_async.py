from domain.entities.user_chat import UserChat
from application.repositories.user_chats_repository import UserChatsRepository
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from typing import List, Optional

from icecream import ic

class PostgresUserChatsRepositoryAsync(UserChatsRepository):
    def __init__(self, db_connection_pool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    async def get_by_id(self, user_id: int, connection=None) -> List[UserChat]:
        result = await connection.fetch(f"SELECT * FROM public.user_chat WHERE user_id = {user_id}")
        return [UserChat(user_id=row['user_id'], role=row['role'], company_code=row['company_code']) for row in result]

    @open_and_close_connection
    async def get_user_id_by_company_code(self, company_code: str, connection=None) -> List[int]:
        query = f'''SELECT public.user_chat.user_id FROM public.user_chat
        JOIN public.company ON public.user_chat.company_id = public.company.company_id
        WHERE public.company.company_code = '{company_code}
        '''
        result = await connection.fetch(query)
        return [row['user_id'] for row in result]


    @open_and_close_connection
    async def get_companies_codes_by_user_id(self, user_id: int, connection=None) -> List[str]:
        query = f'''SELECT public.company.company_code FROM public.user_chat
        JOIN public.company ON public.user_chat.company_id = public.company.company_id
        WHERE public.user_chat.user_id = {user_id}
        '''
        result = await connection.fetch(query)
        return [row['company_code'] for row in result]

    @open_and_close_connection
    async def save_user_chat(self, user_chat: UserChat, connection=None):
        await connection.fetch(
            "INSERT INTO public.user_chat (user_chat_id, role, company_id) "
            "VALUES ($1, $2, (SELECT company_id FROM public.company WHERE company_code = $3))",
            user_chat.user_id, user_chat.role, user_chat.company_code
        )

    @open_and_close_connection
    async def is_user_chat_exists(self, user_chat: UserChat, connection=None) -> bool:
        result = await connection.fetch(
            f"SELECT EXISTS(SELECT 1 FROM public.user_chat "
            f"JOIN public.company ON public.user_chat.company_id = public.company.company_id "
            f"WHERE public.user_chat.user_id = {user_chat.user_id} "
            f"AND public.user_chat.role = '{user_chat.role}' "
            f"AND public.company.company_code = '{user_chat.company_code}')"
        )
        return result[0]['exists'] if result else False
