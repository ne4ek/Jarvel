from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from domain.entities.tunneling_message import TunnelingMessage
from icecream import ic

class PostgresTunnelingAsync:
    def __init__(self, db_connection_pool):
        self._connection_pool = db_connection_pool
     
     
    @open_and_close_connection   
    async def save(self, tunneling_message: TunnelingMessage, connection=None) -> int:
        query = '''INSERT INTO public.tunneling(specify_chat_pinned_message_id, source_chat_pinned_message_id, to_chat_id, to_topic_id, from_chat_id, from_topic_id)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING tunneling_id'''
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        tunneling_id = await connection.fetchval(query, 
                                                 tunneling_message.specify_chat_pinned_message_id,
                                                 tunneling_message.source_chat_pinned_message_id,
                                                 tunneling_message.to_chat_id,
                                                 to_topic_id,
                                                 tunneling_message.from_chat_id,
                                                 from_topic_id,
                                                 )
        return tunneling_id
    
    @open_and_close_connection   
    async def get_by_full_info(self, tunneling_message: TunnelingMessage, connection=None) -> TunnelingMessage | None:
        query = '''SELECT * FROM public.tunneling WHERE to_chat_id = $1 AND to_topic_id = $2 
        AND from_chat_id = $3 AND from_topic_id = $4'''
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        result = await connection.fetch(query, tunneling_message.to_chat_id,
                                         to_topic_id,
                                         tunneling_message.from_chat_id,
                                         from_topic_id,
                                         )

        if result:
            return self.__tunneling_message_from_row(result[0])
    
    @open_and_close_connection
    async def get_by_from_info(self, tunneling_message: TunnelingMessage, connection=None) -> list[TunnelingMessage]:
        query = '''SELECT * FROM public.tunneling WHERE from_chat_id = $1 AND from_topic_id = $2'''
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        result = await connection.fetch(query, tunneling_message.from_chat_id, 
                                        from_topic_id,)
        if not result:
            return []
        tunneling_messages_from_db = []
        for tunneling_message_from_db in result:
            tunneling_messages_from_db.append(self.__tunneling_message_from_row(tunneling_message_from_db))
        return tunneling_messages_from_db

        
    def __tunneling_message_from_row(self, row) -> TunnelingMessage:
        return TunnelingMessage(specify_chat_pinned_message_id = row.get("specify_chat_pinned_message_id"),
                                source_chat_pinned_message_id = row.get("source_chat_pinned_message_id"),
                                to_chat_id = row.get("to_chat_id"),
                                to_topic_id = row.get("to_topic_id") if row.get("to_topic_id") != -1 else None,
                                from_chat_id = row.get("from_chat_id"),
                                from_topic_id = row.get("from_topic_id") if row.get("from_topic_id") != -1 else None,
                                )
    @open_and_close_connection   
    async def delete_all_by_from(self, tunneling_message: TunnelingMessage, connection=None) -> None:
        query = '''DELETE FROM tunneling WHERE from_chat_id = $1 AND from_topic_id = $2'''
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        await connection.fetch(query, tunneling_message.from_chat_id, from_topic_id)

    @open_and_close_connection 
    async def delete_by_full_info(self, tunneling_message: TunnelingMessage, connection=None) -> bool:
        query = "DELETE FROM tunneling WHERE to_chat_id = $1 AND to_topic_id = $2 AND from_chat_id = $3 AND from_topic_id = $4"
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1 
        result = await connection.fetch(query, tunneling_message.to_chat_id,
                                        to_topic_id,
                                        tunneling_message.from_chat_id,
                                        from_topic_id)


        