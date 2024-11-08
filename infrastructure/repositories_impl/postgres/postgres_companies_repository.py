from domain.entities.company import Company
from domain.entities.group_chat import GroupChat
from domain.entities.user import User
from application.repositories.companies_repository import CompaniesRepository
from psycopg2.pool import ThreadedConnectionPool
from typing import List
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
from icecream import ic


class PostgresCompaniesRepository(CompaniesRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    def get_company_code_by_chat_id(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT company_code FROM group_chats WHERE chat_id = '{chat_id}'")
        try:
            company_code = cursor.fetchone()[0]
            print(company_code)
            return company_code
        except:
            return

    @open_and_close_connection
    def save(self, company: Company, conn=None, cursor=None):
        cursor.execute(
            "INSERT INTO companies (code, name, description, owner_id) "
            "VALUES (%s, %s, %s, %s);",
            (company.code, company.name, company.description, company.owner_id),
        )
        conn.commit()

    @open_and_close_connection
    def get_owner_id_by_company_code(self, company_code: str, conn=None, cursor=None):
        cursor.execute(f"SELECT owner_id FROM companies WHERE code = '{company_code}';")
        data = cursor.fetchone()
        print(data)
        return data

    @open_and_close_connection
    def get_codes(self, conn=None, cursor=None):
        cursor.execute("SELECT code FROM companies;")
        data = [item[0] for item in cursor.fetchall()]
        print(data)
        return data

    @open_and_close_connection
    def is_company_code_exists(self, company_code: str, conn=None, cursor=None) -> bool:
        cursor.execute(f"SELECT EXISTS(SELECT code from companies WHERE code = '{company_code}');")
        data = cursor.fetchone()[0]
        print(data)
        return data

    @open_and_close_connection
    def is_group_registered_in_company(self, chat: GroupChat, conn=None, cursor=None) -> bool:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM group_chats WHERE chat_id = '{chat.chat_id}' AND company_code = '{chat.company_code}')")
        data = cursor.fetchone()[0]
        print(data)
        return data


    @open_and_close_connection
    def get_code_and_owner_id(self, conn=None, cursor=None):
        cursor.execute("SELECT code, owner_id FROM companies;")
        data = cursor.fetchall()
        print(data)
        return data

    @open_and_close_connection
    def get_users_id_by_company_code(self, company_code: str, conn=None, cursor=None):
        cursor.execute(f"SELECT users_id FROM companies WHERE code = '{company_code}';")
        data = cursor.fetchone()
        print(data)
        return data

    @open_and_close_connection
    def get_owner_id_by_company_code(self, company_code: str, conn=None, cursor=None):
        cursor.execute(f"SELECT owner_id FROM companies WHERE code = '{company_code}';")
        data = cursor.fetchone()[0]
        print(data)
        return data

    @open_and_close_connection
    def add_user_id_by_company_code(self, user_id: int, company_code: str, conn=None, cursor=None):
        cursor.execute(
            f"UPDATE companies SET users_id = users_id || {user_id} where code = '{company_code}'"
        )
        conn.commit()

    @open_and_close_connection
    def get_name_by_company_code(self, company_code: str, conn=None, cursor=None):
        
        cursor.execute(f"SELECT name FROM companies WHERE code='{company_code}';")
        data = cursor.fetchone()[0]
        print(data)
        return data

    @open_and_close_connection
    def get_names_by_user_id(self, user_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT name FROM companies WHERE '{user_id}' = ANY (users_id);")
        data = [name[0] for name in cursor.fetchall()]
        print(data)
        return data

    @open_and_close_connection
    def get_names_by_owner_id(self, owner_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT name FROM companies WHERE owner_id = '{owner_id}';")
        data = [name[0] for name in cursor.fetchall()]
        print(data)
        return data

    @open_and_close_connection
    def get_description_by_company_code(self, company_code: str, conn=None, cursor=None):
        cursor.execute(f"SELECT description FROM companies WHERE code = '{company_code}';")
        data = cursor.fetchone()[0]
        print(data)
        return data

    @open_and_close_connection
    def get_users_ids_by_company_code(self, company_code: str, conn=None, cursor=None):
        pass

    @open_and_close_connection
    def add_group_chat_to_company(self, chat: GroupChat, conn=None, cursor=None):
        cursor.execute(
        "INSERT INTO group_chats (chat_id, name, company_code, owner_id) "
        "VALUES (%s, %s, %s, %s);",
        (chat.chat_id, chat.name, chat.company_code, chat.owner_id),
        )
        conn.commit()
    
    @open_and_close_connection
    def get_users_by_company_code(self, company_code: str, conn=None, cursor=None) -> List[User]:
        cursor.execute(f"""
                        SELECT * FROM users
                        JOIN companies ON users.user_id = ANY(companies.users_id)
                        WHERE companies.code = '{company_code}';
                        """)
        data = cursor.fetchall()
        users = []
        for user in data:
            users.append(User(user_id=user[0],
                              username=user[1],
                              full_name=user[2],
                              email=user[3],
                              personal_link=user[4]))
        print(data)
        return users
        
    @open_and_close_connection
    def get_owner_by_company_code(self, company_code: str, conn=None, cursor=None) -> User:
        cursor.execute(f"""
                         SELECT * FROM users
                         JOIN companies ON users.user_id = companies.owner_id
                         WHERE companies.code = '{company_code}';
                         """)
        
        data = cursor.fetchall()
        if not data:
            return
        data = data[0]
        owner = User(user_id=data[0],
                     username=data[1],
                     full_name=data[2],
                     email=data[3],
                     personal_link=data[4])
        print(owner)
        return owner
    
    def is_user_registered_in_company(self, company_code: str, user_id: int) -> bool:
        return