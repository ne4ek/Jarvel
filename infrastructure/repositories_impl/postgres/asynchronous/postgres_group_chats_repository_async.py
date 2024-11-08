from domain.entities.group_chat import GroupChat
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from application.repositories.group_chats_repository import GroupChatsRepository
class PostgresGroupChatsRepositoryAsync(GroupChatsRepository):
    def __init__(self, db_connection_pool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    async def get_company_code(self, chat_id: int, connection=None):
        query = f"""
        SELECT public.company.company_code 
        FROM public.group_chat 
        JOIN public.company ON public.group_chat.company_id = public.company.company_id 
        WHERE public.group_chat.group_chat_id = {chat_id}
        """
        result = await connection.fetch(query)
        company_code = result[0]['company_code']
        print(company_code)
        return company_code

    @open_and_close_connection
    async def get_all_chat_ids(self, connection=None):
        query = "SELECT group_chat_id FROM public.group_chat"
        result = await connection.fetch(query)
        chat_ids = [row['group_chat_id'] for row in result]
        print(chat_ids)
        return chat_ids
    
    @open_and_close_connection
    async def get_by_chat_id(self, chat_id: int, connection=None):
        query = f"SELECT * FROM public.group_chat WHERE group_chat_id = {chat_id}"
        result = await connection.fetch(query)
        if not result:
            return None
        row = result[0]
        
        # Получаем company_code и owner_id
        query_company_code = f"""
        SELECT public.company.company_code 
        FROM public.group_chat 
        JOIN public.company ON public.group_chat.company_id = public.company.company_id 
        WHERE public.group_chat.group_chat_id = {chat_id}
        """
        result_company_code = await connection.fetch(query_company_code)
        company_code = result_company_code[0]['company_code'] if result_company_code else None
        
        query_owner_id = f"""
        SELECT public.company.owner_id
        FROM public.group_chat 
        JOIN public.company ON public.group_chat.company_id = public.company.company_id 
        WHERE public.group_chat.group_chat_id = {chat_id}
        """
        result_owner_id = await connection.fetch(query_owner_id)
        owner_id = result_owner_id[0]['owner_id'] if result_owner_id else None

        group_chat = GroupChat(
            chat_id=row['group_chat_id'],
            name=row['name'],
            company_code=company_code,
            owner_id=owner_id
        )
        print(group_chat)
        return group_chat

    @open_and_close_connection
    async def save_group_chat(self, group_chat: GroupChat, connection=None):
        query = f"""
        INSERT INTO public.group_chat (group_chat_id, name, company_id) 
        VALUES ($1, $2, 
        (SELECT company_id FROM public.company WHERE company_code = $3))
        """
        result = await connection.fetch(query, group_chat.chat_id, group_chat.name, group_chat.company_code)
        print(result)

    @open_and_close_connection
    async def is_group_chat_exists(self, group_chat: GroupChat, connection=None):
        query = f"""
        SELECT EXISTS(
            SELECT 1 
            FROM public.group_chat 
            JOIN public.company ON public.group_chat.company_id = public.company.company_id 
            WHERE public.group_chat.group_chat_id = {group_chat.chat_id} 
            AND public.company.company_code = '{group_chat.company_code}'
        )
        """
        result = await connection.fetch(query)
        exists = result[0]['exists']
        print(exists)
        return exists

    @open_and_close_connection
    async def get_name_by_chat_id(self, chat_id: int, connection=None):
        query = f"SELECT name FROM public.group_chat WHERE group_chat_id = {chat_id}"
        result = await connection.fetch(query)
        name = result[0]['name']
        print(name)
        return name

    @open_and_close_connection
    async def delete(self, chat_id: int, connection=None):
        query = f"DELETE FROM public.group_chat WHERE group_chat_id = {chat_id}"
        result = await connection.fetch(query)
        print(result)

    @open_and_close_connection
    async def is_chat_id_exists(self, chat_id: int, connection=None):
        query = f"SELECT EXISTS(SELECT 1 FROM public.group_chat WHERE group_chat_id = {chat_id})"
        result = await connection.fetch(query)
        exists = result[0]['exists']
        print(exists)
        return exists

    @open_and_close_connection
    async def is_group_chat_assigned_to_company(self, chat_id: int, connection=None) -> bool:
        query = f"SELECT EXISTS(SELECT 1 FROM public.group_chat WHERE group_chat_id = {chat_id} AND company_id IS NOT NULL)"
        result = await connection.fetch(query)
        assigned = result[0]['exists']
        print(assigned)
        return assigned
