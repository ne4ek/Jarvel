from application.repositories.arbitrary_user_data_repository import ArbitraryUserDataRepository
# from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from icecream import ic

class PostgresArbitraryUserDataRepositoryAsync(ArbitraryUserDataRepository):
    def __init__(self, db_connection_pool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    async def get_arbitrary_user_data(self, user_id: int, connection=None) -> str:
        result = await connection.fetch(
            "SELECT arbitrary_data::text "
            "FROM public.\"user\" "
            "WHERE user_id = $1;",
            user_id
        )
        return result[0]["arbitrary_data"]

    @open_and_close_connection
    async def set_arbitrary_user_data(self, user_id: int, arbitrary_data: str, connection=None):
        query = \
            '''
            UPDATE public."user"
            SET arbitrary_data = $1::jsonb
            WHERE user_id = $2;
            '''
        await connection.fetch(query, arbitrary_data, user_id)




