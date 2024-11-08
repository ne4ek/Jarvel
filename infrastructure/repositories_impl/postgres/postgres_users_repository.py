from application.repositories.users_repository import UsersRepository
from domain.entities.user import User
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
from psycopg2.pool import ThreadedConnectionPool
from icecream import ic
import json


class PostgresUsersRepository(UsersRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool

    @staticmethod
    @open_and_close_connection
    def get_by_id(user_id: int, conn=None, cursor=None) -> User:
        
        cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}")
        user_data = cursor.fetchone()
        ic(user_data)
        if user_data:
            return User(user_id=user_data[0],
                        username=user_data[1],
                        full_name=user_data[2],
                        email=user_data[3],
                        personal_link=user_data[4])
        else:
            return None

    @staticmethod
    @open_and_close_connection
    def get_by_id_list(user_id_list: list[int], conn=None, cursor=None) -> list[User]:
        cursor.execute(f"SELECT user_id, username, name, email, personal_link, arbitrary_data FROM users WHERE user_id = ANY(%s);", (user_id_list,))
        user_data = cursor.fetchall()
        return [User(user_id=user_data[0],
                     username=user_data[1],
                     full_name=user_data[2],
                     email=user_data[3],
                     personal_link=user_data[4]) for user_data in user_data]


    @staticmethod
    @open_and_close_connection
    def get_full_name_by_id(user_id: int, conn=None, cursor=None) -> str:
        cursor.execute(f"SELECT name FROM users WHERE user_id = {user_id};")
        full_name = cursor.fetchone()
        if full_name:
            return full_name[0]
        return None

    @staticmethod
    @open_and_close_connection
    def is_user_exists(user_id: int, conn=None, cursor=None) -> bool:
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,))
        data = cursor.fetchone()
        return data[0]

    @staticmethod
    @open_and_close_connection
    def get_username_by_id(user_id: int, conn=None, cursor=None) -> str:
        cursor.execute(f"SELECT username FROM users WHERE user_id = {user_id}")
        data = cursor.fetchone()[0]
        return data

    @staticmethod
    @open_and_close_connection
    def get_all_users(conn=None, cursor=None) -> list[set]:
        cursor.execute("SELECT * FROM users")
        data = cursor.fetchall()
        result = []
        for row in data:
            usr = User()
            usr.user_id = row[0]
            usr.username = row[1]
            usr.full_name = row[2]
            usr.email = row[3]
            usr.created_at = row[4]
            usr.personal_link = row[5]
            usr.arbitrary_data = row[6]
            result.append(usr)
        return result

    @staticmethod
    @open_and_close_connection
    def get_email_by_id(user_id: str, conn=None, cursor=None):
        cursor.execute(f"SELECT email FROM users WHERE user_id = {user_id}")
        data = cursor.fetchone()[0]
        return data

    @staticmethod
    @open_and_close_connection
    def get_name_by_id(user_id: int, conn=None, cursor=None) -> str:
        cursor.execute("SELECT name FROM users WHERE user_id = {}".format(user_id))
        date = cursor.fetchone()[0]
        return date

    @staticmethod
    @open_and_close_connection
    def save(user: User, conn=None, cursor=None) -> None:
        cursor.execute(
            "INSERT INTO users (user_id, username, name, email, arbitrary_data) VALUES (%s, %s, %s, %s, %s::jsonb);",
            (
                user.user_id,
                user.username,
                user.full_name,
                user.email,
                json.dumps({"Имя и фамилия": user.full_name,
                            "Почта": user.email,
                            "Телеграм": user.username,
                            "Номер телефона": None,
                            "Персональная ссылка": None,
                            "Город проживания": None,
                            })
            ),
        )
        conn.commit()
        # Добавить запись в json со словарем популярных ключей

    @staticmethod
    @open_and_close_connection
    def update(user: User, conn=None, cursor=None) -> None:
        cursor.execute(
            f"UPDATE users SET username = '{user.username}', name = '{user.full_name}', email = '{user.email}' WHERE user_id = {user.user_id}"
        )
        conn.commit()

    @staticmethod
    @open_and_close_connection
    def save_personal_link(user_id: int, personal_link: str, conn=None, cursor=None) -> None:
        cursor.execute(f"UPDATE users SET personal_link = '{personal_link}' WHERE user_id = {user_id}")
        conn.commit()

    @staticmethod
    @open_and_close_connection
    def save_email(user_id: int, email: str, conn=None, cursor=None) -> None:
        cursor.execute(f"UPDATE users SET email = '{email}' WHERE user_id = {user_id}")
        conn.commit()
        
    @staticmethod
    @open_and_close_connection
    def is_user_registered_in_company(user_id: int, company_code: str, conn=None, cursor=None) -> bool:
        # Could be better, but there're things far worse in this application. 
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM companies WHERE (%s = ANY(users_id) OR owner_id = %s) AND code = %s)",
                       (user_id, user_id, company_code))
        res = cursor.fetchone()[0]
        return res