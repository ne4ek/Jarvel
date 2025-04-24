from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from domain.entities.tunneling_message import TunnelingMessage
from icecream import ic

class PostgresTunnelingAsync:
    def __init__(self, db_connection_pool):
        self._connection_pool = db_connection_pool
     
     
    @open_and_close_connection   
    async def save(self, tunneling_message: TunnelingMessage, connection=None) -> int:
        query = '''INSERT INTO public.tunneling(specify_chat_pinned_message_id, source_chat_pinned_message_id, to_chat_id, to_topic_id, from_chat_id, from_topic_id, tunnel_type, is_active, user_id, company_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) RETURNING tunneling_id'''
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        tunneling_id = await connection.fetchval(query, 
                                                 tunneling_message.specify_chat_pinned_message_id,
                                                 tunneling_message.source_chat_pinned_message_id,
                                                 tunneling_message.to_chat_id,
                                                 to_topic_id,
                                                 tunneling_message.from_chat_id,
                                                 from_topic_id,
                                                 tunneling_message.tunnel_type,
                                                 tunneling_message.is_active,
                                                 tunneling_message.user_id,
                                                 tunneling_message.company_id
                                                 )
        return tunneling_id
    
    @open_and_close_connection   
    async def get_any_by_full_info(self, tunneling_message: TunnelingMessage, connection=None) -> TunnelingMessage | None:
        query = '''SELECT * FROM public.tunneling WHERE to_chat_id = $1 AND to_topic_id = $2 
        AND from_chat_id = $3 AND from_topic_id = $4'''
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        ic(tunneling_message)
        result = await connection.fetch(query, tunneling_message.to_chat_id,
                                         to_topic_id,
                                         tunneling_message.from_chat_id,
                                         from_topic_id,
                                         )
        
        if result:
            return self.__tunneling_message_from_row(result[0])
    
    @open_and_close_connection
    async def get_active_by_full_info(self, tunneling_message: TunnelingMessage, connection=None) -> TunnelingMessage | None:
        query = '''SELECT * FROM public.tunneling WHERE to_chat_id = $1 AND to_topic_id = $2 
        AND from_chat_id = $3 AND from_topic_id = $4 AND is_active = true'''
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
    async def get_any_by_from_info(self, tunneling_message: TunnelingMessage, connection=None) -> list[TunnelingMessage]:
        query = '''SELECT * FROM public.tunneling WHERE from_chat_id = $1 AND from_topic_id = $2'''
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        result = await connection.fetch(query, tunneling_message.from_chat_id, 
                                        from_topic_id,)
        return self.__list_tunneling_message_from_row(result)
    
    @open_and_close_connection
    async def __get_any_by_from_info(self, tunneling_message: TunnelingMessage, connection=None) -> list[TunnelingMessage]:
        pass # TODO: implement
        
    def __tunneling_message_from_row(self, row) -> TunnelingMessage:
        return TunnelingMessage(tunneling_id = row.get("tunneling_id"),
                                specify_chat_pinned_message_id = row.get("specify_chat_pinned_message_id"),
                                source_chat_pinned_message_id = row.get("source_chat_pinned_message_id"),
                                to_chat_id = row.get("to_chat_id"),
                                to_topic_id = row.get("to_topic_id") if row.get("to_topic_id") != -1 else None,
                                from_chat_id = row.get("from_chat_id"),
                                from_topic_id = row.get("from_topic_id") if row.get("from_topic_id") != -1 else None,
                                tunnel_type = row.get("tunnel_type"),
                                is_active = row.get("is_active"),
                                company_id = row.get("company_id"),
                                user_id = row.get("user_id"),
                                )
        
    def __list_tunneling_message_from_row(self, row) -> list[TunnelingMessage]:
        if not row:
            return []
        tunneling_messages_from_db = []
        for tunneling_message_from_db in row:
            tunneling_messages_from_db.append(self.__tunneling_message_from_row(tunneling_message_from_db))
        return tunneling_messages_from_db
    
    
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
        
        
    @open_and_close_connection
    async def get_full_by_chat_topic_id(self, chat_id, topic_id, connection=None) -> tuple[list[TunnelingMessage]]:
        query_for_to_chat  = "SELECT * FROM tunneling WHERE to_chat_id = $1 AND to_topic_id = $2"
        query_for_from_chat = "SELECT * FROM tunneling WHERE from_chat_id = $1 AND from_topic_id = $2"
        topic_id = topic_id if topic_id is not None else -1
        result_for_to_chat = await connection.fetch(query_for_to_chat, chat_id, topic_id)
        result_for_from_chat = await connection.fetch(query_for_from_chat, chat_id, topic_id)

        list_for_to_chat = self.__list_tunneling_message_from_row(result_for_to_chat)
        list_for_from_chat = self.__list_tunneling_message_from_row(result_for_from_chat)
        return (list_for_to_chat, list_for_from_chat)

    @open_and_close_connection
    async def get_full_by_chat_id(self, chat_id, connection=None) -> tuple[list[TunnelingMessage]]:
        query_for_to_chat  = "SELECT * FROM tunneling WHERE to_chat_id = $1"
        query_for_from_chat = "SELECT * FROM tunneling WHERE from_chat_id = $1"
        result_for_to_chat = await connection.fetch(query_for_to_chat, chat_id)
        result_for_from_chat = await connection.fetch(query_for_from_chat, chat_id)

        list_for_to_chat = self.__list_tunneling_message_from_row(result_for_to_chat)
        list_for_from_chat = self.__list_tunneling_message_from_row(result_for_from_chat)
        return (list_for_from_chat, list_for_to_chat)

    @open_and_close_connection
    async def get_by_id(self, tunneling_id: int, connection=None) -> TunnelingMessage | None:
        query = "SELECT * FROM tunneling WHERE tunneling_id = $1"
        result = await connection.fetch(query, int(tunneling_id))
        if result:
            return self.__tunneling_message_from_row(result[0])
        else:
            return None
        

    @open_and_close_connection
    async def update_pinned_message_ids_by_tunneling_id(self, tunneling_message: TunnelingMessage, connection=None) -> None:
        query = "UPDATE tunneling SET specify_chat_pinned_message_id = $1, source_chat_pinned_message_id = $2 WHERE tunneling_id = $3"
        await connection.fetch(query, tunneling_message.specify_chat_pinned_message_id,
                              tunneling_message.source_chat_pinned_message_id,
                              tunneling_message.tunneling_id)

    @open_and_close_connection
    async def get_all_by_user_id(self, user_id: int, connection=None) -> list[TunnelingMessage]:
        query = "SELECT * FROM tunneling WHERE user_id = $1"
        result = await connection.fetch(query, user_id)
        return self.__list_tunneling_message_from_row(result)

    @open_and_close_connection
    async def update_is_active_by_id(self, tunneling_id: int, is_active: bool, connection=None) -> None:
        query = "UPDATE tunneling SET is_active = $1 WHERE tunneling_id = $2"
        await connection.fetch(query, is_active, int(tunneling_id))

    @open_and_close_connection
    async def delete_by_id(self, tunneling_id: int, connection=None) -> None:
        query = "DELETE FROM tunneling WHERE tunneling_id = $1"
        await connection.fetch(query, int(tunneling_id))

    @open_and_close_connection
    async def delete_by_full_info(self, tunneling_message: TunnelingMessage, connection=None) -> None:
        query = "DELETE FROM tunneling WHERE to_chat_id = $1 AND to_topic_id = $2 AND from_chat_id = $3 AND from_topic_id = $4"
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        await connection.fetch(query, tunneling_message.to_chat_id, to_topic_id, tunneling_message.from_chat_id, from_topic_id)

    @open_and_close_connection
    async def update_is_active_by_full_info(self, tunneling_message: TunnelingMessage, is_active: bool, connection=None) -> None:
        query = "UPDATE tunneling SET is_active = $1 WHERE to_chat_id = $2 AND to_topic_id = $3 AND from_chat_id = $4 AND from_topic_id = $5"
        to_topic_id = tunneling_message.to_topic_id if tunneling_message.to_topic_id is not None else -1
        from_topic_id = tunneling_message.from_topic_id if tunneling_message.from_topic_id is not None else -1
        await connection.fetch(query, is_active, tunneling_message.to_chat_id, to_topic_id, tunneling_message.from_chat_id, from_topic_id)
