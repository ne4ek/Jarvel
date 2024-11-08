from typing import Union, Dict
from fuzzywuzzy import fuzz
from psycopg2.pool import ThreadedConnectionPool
from application.repositories.arbitrary_user_data_repository import ArbitraryUserDataRepository
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
from icecream import ic


class PostgresArbitaryUserDataRepository(ArbitraryUserDataRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    def get_arbitrary_user_data(self, user_id:int, conn=None, cursor=None) -> str:
        cursor.execute("SELECT arbitrary_data::text "
                       f"FROM users WHERE user_id = {user_id};")
        user_data = cursor.fetchone()
        return user_data[0]
    
    @open_and_close_connection
    def set_arbitrary_user_data(self, user_id: int, arbitrary_data: str, conn=None, cursor= None):
        query = \
'''
UPDATE users
SET arbitrary_data = %s::jsonb
WHERE user_id = %s;
'''
        cursor.execute(query, (arbitrary_data, user_id))
        conn.commit()

    #open_and_close_connection
    #ef get_arbitrary_user_data_value_by_key(self, user_id:int, key:str, conn=None, cursor=None) -> str:
    #   cursor.execute(f"SELECT jsonb_extract_path_text(arbitrary_data, {key}) FROM users WHERE user_id={user_id};")
    #   value = cursor.fetchone()[0]
    #   return value

    #ef __search_arbitrary_mentioned_data(self, user_id: int, mentioned_data: str) -> str:
    #   if mentioned_data == "0":
    #       return None
    #   all_user_data = self.get_arbitrary_all_user_data(user_id)
    #   similiar_data = {}
    #   for data in all_user_data:
    #       ratio = fuzz.WRatio(mentioned_data, all_user_data)
    #       if ratio == 100:
    #           return data
    #       elif ratio >= 70:
    #           if ratio not in similiar_data.keys():
    #               similiar_data[ratio] = []
    #           similiar_data[ratio].append(data)
    #   try:
    #       ratio = max(similiar_data.keys())
    #       return similiar_data[ratio][0]
    #   except:
    #       return None

    #open_and_close_connection
    #ef create_empty_arbitrary_user_data(self, user_id:int, conn=None, cursor=None) -> None:
    #   cursor.execute("UPDATE users SET arbitrary_data = '{}'::jsonb "
    #                  f"WHERE user_id = {user_id};")
    #   create_empty_data = cursor.fetchall()
    #   return create_empty_data

    #open_and_close_connection
    #ef update_arbitrary_user_data(self, user_id:int, new_data:Union[Dict[str, str], str], conn=None, cursor=None):
    #   #получаем все ключи из json, сравниваем с ключем новой записи.
    #   # Если нет совпадений, записываем в json ключ-значение.
    #   # Если есть добавляем значения к этому ключу {'faw_color':['синий', 'зеленый' ...]}
    #   data_keys = cursor.execute("SELECT jsonb_object_keys(arbitrary_data), "
    #                              f"FROM users WHERE user_id = {user_id};")
    #   key_new_data = new_data.keys()
    #   #similiar_data = {}
    #   for key in data_keys:
    #       ratio = fuzz.WRatio(key_new_data, data_keys)
    #       if ratio == 100:
    #           cursor.execute(f"UPDATE users SET arbitrary_data=('{new_data}')::jsonb WHERE user_id={user_id};")
    #       else:
    #           cursor.execute(f"INSERT INTO users(arbitrary_data) VALUES {new_data}::jsonb WHERE user_id={user_id};")

    #   #cursor.execute(f"UPDATE users SET arbitrary_data = json_build_object({new_data}) WHERE user_id={user_id})")
    #   # добавить поиск ключа в json перед добавлением нового значения
    #   # {





