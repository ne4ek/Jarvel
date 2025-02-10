from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from icecream import ic

class PostgresMediaGroupRepositoryAsync:
    def __init__(self, db_connection_pool):
        self._connection_pool = db_connection_pool

    @open_and_close_connection
    async def save(self, media_group_id: int, connection=None) -> None:
        query = "INSERT INTO public.media_group(media_group_id) VALUES ($1)"
        await connection.fetch(query, int(media_group_id))


    @open_and_close_connection
    async def is_exists(self, media_group_id: int, connection=None) -> bool:
        query = "SELECT * FROM public.media_group WHERE media_group_id = $1"
        result = await connection.fetch(query, int(media_group_id))
        if not result:
            await self.save(media_group_id)
        return bool(result)
    