from application.repositories.companies_repository import CompaniesRepository
from domain.entities.company import Company
from domain.entities.group_chat import GroupChat
from domain.entities.user import User
from asyncpg.pool import Pool
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from icecream import ic

class PostgresCompaniesRepositoryAsync(CompaniesRepository):
    def __init__(self, connection_pool: Pool):
        self._connection_pool = connection_pool

    @open_and_close_connection
    async def get_company_code_by_chat_id(self, chat_id: int, connection=None):
        query = f"""SELECT public.company.company_code
                    FROM public.group_chat
                    JOIN public.company ON public.group_chat.company_id = public.company.company_id
                    WHERE public.group_chat.group_chat_id = {chat_id}"""
        result = await connection.fetch(query)
        try:
            company_code = result[0].get("company_code")
        except:
            return
        return company_code

    @open_and_close_connection
    async def get_owner_id_by_company_code(self, company_code, connection=None):
        query = f"""
                SELECT public.company.owner_id
                FROM public.company
                WHERE public.company.company_code = '{company_code}'"""
        result = await connection.fetch(query)
        owner_id = result[0].get("owner_id")
        print(owner_id)
        return owner_id

    @open_and_close_connection
    async def _add_owner(self, owner_id, company_id, connection=None):
        query = f"""INSERT INTO public.user_company (user_id, company_id)
                    VALUES ({owner_id}, {company_id});"""
        result = await connection.fetch(query)
        print(result)

    @open_and_close_connection
    async def save(self, company_obj: Company, connection=None):
        company_query = f"""
        INSERT INTO public.company (name, company_code, description, owner_id)
        VALUES ($1, $2, $3, $4)
        RETURNING company_id;
        """
        company_id = await connection.fetch(company_query, company_obj.name, company_obj.code, company_obj.description, company_obj.owner_id)
        company_id = company_id[0].get("company_id")
        user_company_query = f"""
        INSERT INTO public.user_company (user_id, company_id, role, rights) 
        VALUES ($1, $2, $3, $4);
        """
        await connection.execute(user_company_query, company_obj.owner_id, company_id, "owner", "owner")
        

    @open_and_close_connection
    async def get_codes(self, connection=None):
        query = """SELECT public.company.company_code FROM public.company"""
        result = await connection.fetch(query)
        codes = [code.get("company_code") for code in result]
        print(codes)
        return codes

    @open_and_close_connection
    async def is_company_code_exists(self, company_code, connection=None):
        query = f"""SELECT EXISTS (
                    SELECT 1
                    FROM public.company
                    WHERE public.company.company_code = '{company_code}'
                    );"""
        result = await connection.fetch(query)
        exists = result[0].get("exists")
        print(exists)
        return exists

    @open_and_close_connection
    async def is_user_registered_in_company(self, company_code: str, user_id: int, connection=None):
        query = f"""SELECT EXISTS (
                    SELECT 1
                    FROM public.user_company
                    JOIN public.company ON public.user_company.company_id = public.company.company_id
                    WHERE public.user_company.user_id = $1 AND public.company.company_code = $2)"""
        result = await connection.fetch(query, user_id, company_code)
        exists = result[0].get("exists")
        ic(exists)
        return exists

    @open_and_close_connection
    async def is_group_registered_in_company(self, chat: GroupChat, connection=None):
        query = f"""SELECT EXISTS (
                    SELECT 1
                    FROM public.group_chat
                    JOIN public.company ON public.group_chat.company_id = public.company.company_id
                    WHERE public.group_chat.group_chat_id = {chat.chat_id}
                    AND public.company.company_code = '{chat.company_code}'
                    );"""
        result = await connection.fetch(query)
        exists = result[0].get("exists")
        ic(exists)
        return exists

    @open_and_close_connection
    async def get_code_and_owner_id(self, connection=None):
        query = """SELECT company_code, owner_id FROM public.company"""
        result = await connection.fetch(query)
        print(result)
        return result

    @open_and_close_connection
    async def get_users_id_by_company_code(self, company_code: str, connection=None):
        query = f"""SELECT public.user.user_id
                    FROM public.user
                    JOIN public.user_company ON public.user.user_id = public.user_company.user_id
                    JOIN public.company ON public.user_company.company_id = public.company.company_id
                    WHERE public.company.company_code = '{company_code}';"""
        result = await connection.fetch(query)
        user_ids = [user.get("user_id") for user in result]
        print(user_ids)
        return user_ids

    @open_and_close_connection
    async def add_user_id_by_company_code(self, user_id=int, company_code=str, role=str, connection=None):
        company_id_query = f"SELECT company_id FROM public.company WHERE company_code = '{company_code}';"
        company_id = await connection.fetch(company_id_query)
        company_id = company_id[0].get("company_id")
        query = f"""INSERT INTO public.user_company (user_id, company_id, role, rights)
                    VALUES ($1, $2, $3, 'user');"""
        user_id = await connection.fetch(query, user_id, company_id, role)
        ic(user_id)

    @open_and_close_connection
    async def get_name_by_company_code(self, company_code, connection=None):
        query = f"""SELECT public.company.name
                    FROM public.company
                    WHERE public.company.company_code = '{company_code}';"""
        result = await connection.fetch(query)
        name = result[0].get("name")
        return name

    @open_and_close_connection
    async def get_names_by_user_id(self, user_id, connection=None):
        query = f"""SELECT public.company.name
                    FROM public.company
                    JOIN public.user_company ON public.company.company_id = public.user_company.company_id
                    WHERE public.user_company.user_id = {user_id};"""
        result = await connection.fetch(query)
        names = [name.get("name") for name in result]
        print(names)
        return names

    @open_and_close_connection
    async def get_names_by_owner_id(self, owner_id: int, connection=None):
        query = f"""SELECT public.company.name
                    FROM public.company
                    WHERE public.company.owner_id = {owner_id};"""
        result = await connection.fetch(query)
        names = [name.get("name") for name in result]
        print(names)
        return names

    @open_and_close_connection
    async def get_description_by_company_code(self, company_code, connection=None):
        query = f"""SELECT public.company.description
                    FROM public.company
                    WHERE public.company.company_code = '{company_code}';"""
        result = await connection.fetch(query)
        description = result[0].get("description")
        print(description)
        return description

    @open_and_close_connection
    async def add_group_chat_to_company(self, chat: GroupChat, connection=None):
        query = f"""INSERT INTO public.group_chat (group_chat_id, name, company_id)
                    SELECT {chat.chat_id}, '{chat.name}', public.company.company_id
                    FROM public.company
                    WHERE public.company.company_code = '{chat.company_code}';"""
        result = await connection.fetch(query)
        print(result)

    @open_and_close_connection
    async def get_users_by_company_code(self, company_code: str, connection=None):
        query = f"""SELECT public.user.user_id, public.user.username, public.user.first_name, public.user.last_name, public.user.email
                    FROM public.user
                    JOIN public.user_company ON public.user.user_id = public.user_company.user_id
                    JOIN public.company ON public.user_company.company_id = public.company.company_id
                    WHERE public.company.company_code = '{company_code}';"""
        result = await connection.fetch(query)
        users = [User(user_id=user.get("user_id"), username=user.get("username"), first_name=user.get("first_name"), last_name=user.get("last_name"), email=user.get("email"), full_name=user.get("full_name")) for user in result]
        return users

    @open_and_close_connection
    async def get_owner_by_company_code(self, company_code: str, connection=None):
        query = f"""SELECT public.user.user_id, public.user.username, public.user.first_name, public.user.last_name, public.user.email
                    FROM public.user
                    JOIN public.company ON public.user.user_id = public.company.owner_id
                    WHERE public.company.company_code = '{company_code}';"""
        result = await connection.fetch(query)
        if not result:
            return None
        owner_data = result[0]
        owner = User(user_id=owner_data.get("user_id"), username=owner_data.get("username"), first_name=owner_data.get("first_name"), last_name=owner_data.get("last_name"), email=owner_data.get("email"))
        print(owner)
        return owner


    @open_and_close_connection
    async def get_companies_codes_by_user_id(self, user_id: int, connection=None):
        query = f'''SELECT c.company_code
                    FROM user_company uc
                    JOIN company c
                    ON uc.company_id = c.company_id
                    WHERE uc.user_id = {user_id};'''
        result = await connection.fetch(query)
        if not result:
            return None
        return result


    @open_and_close_connection
    async def get_companies_names_and_codes_by_user_id(self, user_id: int, connection=None):
        query = f'''SELECT c.name, c.company_code
                    FROM user_company uc
                    JOIN company c
                    ON uc.company_id = c.company_id
                    WHERE uc.user_id = {user_id};'''
        result = await connection.fetch(query)
        ic(result)
        if not result:
            return None
        return result
    

    @open_and_close_connection
    async def get_company_code_by_company_id(self, company_id: int, connection=None):
        query = f'''SELECT public.company.company_code FROM public.company WHERE public.company.company_id = {company_id}'''
        result = await connection.fetch(query)
        return result
    

    @open_and_close_connection
    async def get_companies_names_and_codes_by_user_id_role_owner(self, user_id:int,  connection=None):
        query = f'''SELECT c.name, c.company_code
                    FROM user_company uc
                    JOIN company c
                    ON uc.company_id = c.company_id
                    WHERE uc.user_id = {user_id} AND uc.rights = 'owner';'''
        result = await connection.fetch(query)
        if not result:
            return None
        return result
    

    @open_and_close_connection
    async def get_companies_names_and_codes_by_user_id_role_user(self, user_id:int,  connection=None):
        query = f'''SELECT c.name, c.company_code
                    FROM user_company uc
                    JOIN company c
                    ON uc.company_id = c.company_id
                    WHERE uc.user_id = {user_id} AND uc.rights = 'user';'''
        result = await connection.fetch(query)
        if not result:
            return None
        return result