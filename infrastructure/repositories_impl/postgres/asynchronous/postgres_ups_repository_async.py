from domain.entities.up_message import UpMessage
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from icecream import ic
from datetime import timedelta, datetime


class PostgresUpRepositoryAsync:
    def __init__(self, db_connection_pool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    async def save(self, up_message: UpMessage, connection=None) -> int:
        query = '''INSERT INTO public.ups (chat_id, start_date, next_up_date, interval, 
        starting_interval, up_username, reply_message_id, fyi_username, present_date, is_active)
        VALUES ($1, $2, $3, $4::INTERVAL, $5::INTERVAL, $6, $7, $8, $9, $10)
        RETURNING up_id'''
        up_id = await connection.fetchval(query,
                                 up_message.chat_id,
                                 up_message.start_date,
                                 up_message.next_up_date,
                                 up_message.interval,
                                 up_message.starting_interval,
                                 up_message.up_username,
                                 up_message.reply_message_id,
                                 up_message.fyi_username,
                                 up_message.present_date,
                                 up_message.is_active,
                                 )
        return up_id
        
    @open_and_close_connection
    async def get_all(self, connection=None):
        query = "SELECT * FROM public.ups"
        result = await connection.fetch(query)
        ups = []
        for row in result:
            ups.append(self.__up_message_from_row(row))
        return ups
    
    @open_and_close_connection
    async def update_time(self, up_message: UpMessage, connection=None):
        query = "UPDATE public.ups SET interval=$1, next_up_date=$2, present_date=$3 WHERE up_id = $4"
        await connection.execute(query, up_message.interval, up_message.next_up_date, up_message.present_date, up_message.up_message_id)
        
    @open_and_close_connection
    async def get_by_up_id(self, up_id: int, connection=None) -> UpMessage:
        query = "SELECT * FROM public.ups WHERE up_id=$1"
        result = await connection.fetch(query, up_id)
        return self.__up_message_from_row(result)
    
    def __up_message_from_row(self, row) -> UpMessage:
        return UpMessage(
                up_message_id=row.get("up_id"),
                start_date=row.get("start_date"),
                next_up_date=row.get("next_up_date"),
                present_date=row.get("present_date"),
                interval=row.get("interval"),
                starting_interval=row.get("starting_interval"),
                chat_id=row.get("chat_id"),
                up_username=row.get("up_username"),
                reply_message_id=row.get("reply_message_id"),
                bot_message_id=row.get("bot_message_id"),
                fyi_username=row.get("fyi_username"),
                is_active=row.get("is_active"),
            )
    
    @open_and_close_connection
    async def get_up_by_username_and_chat_id(self, username, chat_id, connection=None) -> UpMessage | None:
        query = "SELECT * from public.ups WHERE up_username = $1 AND chat_id = $2 AND is_active = true"
        result = await connection.fetch(query, username, chat_id)
        if result:
            return self.__up_message_from_row(result[0])
    
    @open_and_close_connection
    async def deactivate_up(self, up_id: int, connection=None):
        query = "UPDATE public.ups SET is_active = false WHERE up_id = $1"
        await connection.execute(query, up_id)
        

    @open_and_close_connection
    async def add_bot_id_by_up_id(self, bot_message_id: int, up_id: int, connection=None) -> None:
        query = "UPDATE ups SET bot_message_id = $1 WHERE up_id = $2"
        await connection.execute(query, bot_message_id, up_id)