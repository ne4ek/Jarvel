from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from domain.entities.tunneling_message import TunnelingMessage

class PostgresTunnelingAsync:
    def __init__(self, db_connection_pool):
        self._connection_pool = db_connection_pool
     
     
    @open_and_close_connection   
    async def save(self, tunneling_message: TunnelingMessage, connection=None) -> int:
        query = '''INSERT INTO public.tunneling(to_chat_id, to_topic_id, from_chat_id, from_topic_id)
        VALUES ($1, $2, $3, $4) RETURNING tunneling_id'''
        tunneling_id = await connection.fetchval(query, tunneling_message.to_chat_id,
                                                 tunneling_message.to_topic_id,
                                                 tunneling_message.from_chat_id,
                                                 tunneling_message.from_topic_id)
        return tunneling_id
