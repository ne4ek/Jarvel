import random

from db.postgresql_handlers.companies_db_handler import get_code_from_companies
from db.postgresql_handlers.users_db_handler import get_all_about_users_from_company, get_all_about_owner_from_company
from datetime import datetime, timedelta
from ics import Calendar, Event
from icecream import ic
from pymorphy3 import MorphAnalyzer
from fuzzywuzzy import fuzz
import json
"""
If you don't know where your function belongs, just put it here. We'll sort them in the nearest future.
"""

tag = "auxiliary"


async def generate_code(word_list: list):
    """
    Generates a random code for the company.

    :param list[str] word_list: The list of words to generate.
    :return: A random code for the company.
    :rtype: str
    """
    code = "".join(random.choices(word_list, k=2))

    existing_codes = get_code_from_companies()
    while code in existing_codes:
        code = "".join(random.choices(word_list, k=2))
    return code



def convert_from_datetime(datetime_obj):
    """
    Фукнция конвертирует string в datetime
    :param datetime datetime_obj: Объект datetime
    :return str: Datetime Object
    """
    
    return datetime_obj.strftime("%d.%m.%Y %H:%M")


def update_time_difference(new_datetime, time_diff):
    """
    Функция добавляет к объекту datetime разницу по времени
    :param datetime new_datetime: datetime
    :param timedelta time_diff: timedelta
    :return datetime: datetime
    """
    
    return new_datetime - time_diff


def create_ics_file(meeting_id: int, topic: str, begin: datetime, duration: str = "30"):
    """
    Функция создаёт ics документ, чтобы можно добавить встречу в любой календарь
    :param int meeting_id:
    :param str topic:
    :param datetime begin:
    :param datetime end:
    :param str duration: 
    """
    # Создаем календарь
    calendar = Calendar()
    # ic(calendar)

    # Создаем событие
    e = Event()
    e.name = topic
    e.begin = begin
    e.end = begin + timedelta(minutes=float(duration))
    e.uid = f"jarvel_meeting_{meeting_id}"
    e.created = datetime.now()

    ic(e)

    # Добавляем событие в календарь
    calendar.events.add(e)
    ic(calendar)

    # Сохраняем календарь в файл
    with open(f'storage/calendar_files/meeting_reminder_{meeting_id}.ics', 'w', encoding='utf-8') as f:
        f.writelines(calendar.serialize())


def normalize_names(names: list | dict | str) -> dict:
    """
    Функция приводит имена пользователей к единому виду
    :param list | dict names: Имена пользователей
    :return dict: Нормализованные имена пользователей, отсортированные по родам (мужской, женский, средний)
    """
    if isinstance(names, dict):
        names = list(names.values())
    elif isinstance(names, str):
        names = [names]
    morph = MorphAnalyzer()
    normalized_names = {"masc": [], "fem": [], "neut": [], "other": []}
    
    for name in names:
        name = name.strip()
        if not name:
            continue
        try:
            if len(name.split()) <= 2:
                full_name = name.split()
                gender = None
                for i in range(len(full_name)):
                    parsed_word = morph.parse(full_name[i])[0]
                    full_name[i] = full_name[i].capitalize()
                    if not gender:
                        if 'masc' in parsed_word.tag:
                            gender = "masc"
                        elif 'femn' in parsed_word.tag:
                            gender = "fem"
                        elif 'neut' in parsed_word.tag:
                            gender = "neut"
                        else:
                            gender = "other"
                normalized_names[gender].append(" ".join(full_name))
        except Exception as e:
            
            normalized_names["other"].append(name)
    
    return get_names_full(normalized_names)


def get_names_full(names: dict) -> list:
    """
    Функция объединяет имена пользователей в один список
    :param dict names: Имена пользователей, отсортированные по родам
    :return list: Список имен пользователей
    """
    names_full = []
    if not names:
        return []
    if names["other"] or names["neut"]:
        names["other"].sort()
        names_dataset = json.loads(open("storage/names_dataset.json", "r", encoding="utf-8").read())
        for name in [*names["other"], *names["neut"]]:
            split_name = name.split()
            for i in range(len(split_name)):
                if split_name[i] in names_dataset:
                    split_name[i] = names_dataset[split_name[i]]
            names_full.append(" ".join(split_name))
                
    if names["masc"]:
        names["masc"].sort()
        male_names_dataset = json.loads(open("storage/male_names_dataset.json", "r", encoding="utf-8").read())
        for name in names["masc"]:
            split_name = name.split()
            for i in range(len(split_name)):
                if split_name[i] in male_names_dataset:
                    split_name[i] = male_names_dataset[split_name[i]]
            names_full.append(" ".join(split_name))
    if names["fem"]:
        names["fem"].sort()
        female_names_dataset = json.loads(open("storage/female_names_dataset.json", "r", encoding="utf-8").read())
        for name in names["fem"]:
            split_name = name.split()
            for i in range(len(split_name)):
                if split_name[i] in female_names_dataset:
                    split_name[i] = female_names_dataset[split_name[i]]
            names_full.append(" ".join(split_name))
    return names_full


def get_mentioned_users_data(mentioned_users, company_code):
    """
    Функция возвращает данные о пользователях, упомянутых в сообщении
    :param list | dict mentioned_users: Имена пользователей
    :param str company_code: Код компании
    :return dict: Список известных и неизвестных пользователей
    """
    normalized_users_names = normalize_names(mentioned_users)
    all_users = get_all_about_users_from_company(company_code)
    all_users.append(tuple(get_all_about_owner_from_company(company_code)))
    # ic(all_users)
    mentioned_users_data = []
    mentioned_unknown_users = []
    for name in normalized_users_names:
        found_users = {}
        for user in all_users:
            ratio = fuzz.WRatio(name, user[2])
            
            if ratio == 100:
                found_users = {ratio: user[0]}
                break
            elif ratio >= 80:
                if ratio not in found_users.keys():
                    found_users[ratio] = []
                found_users[ratio].append(user[0])
        if 100 in found_users.keys():
            mentioned_users_data.append(found_users[100])
            continue
        if len(found_users.values()) == 1:
            mentioned_users_data.append(list(found_users.values())[0][0])
            continue
        try:
            ratio = max(found_users.keys())
            if len(found_users[ratio]) == 1:
                mentioned_users_data.append(found_users[ratio][0])
            else:
                mentioned_users_data.append(found_users[ratio])
        except:
            mentioned_unknown_users.append(name)
    ic(mentioned_users_data, mentioned_unknown_users)
    # It return a list of users data. If u see a list of lists, it means that there are several users with the similar names
    return {"known_participants": mentioned_users_data, "unknown_participants": mentioned_unknown_users}



def get_mentioned_user_id(mentioned_user: str, company_code):
    normalized_name = normalize_names(mentioned_user)
    all_users = get_all_about_users_from_company(company_code=company_code)
    all_users.append(type(get_all_about_owner_from_company(company_code=company_code)))
    # ic(all_users)
    similiar_users = {}
    for user in all_users:
        ratio = fuzz.WRatio(normalized_name, user[2])
        
        if ratio == 100:
            return user[0]
        elif ratio >= 80:
            if ratio not in similiar_users.keys():
                similiar_users[ratio] = []
            similiar_users[ratio].append(user[0])
    try:
        ratio = max(similiar_users.keys())
        return similiar_users[ratio][0]
    except:
        return 0

'''
mentined_users = ["Виноградов Максим", "Антон", "Александр"]
all_users = [
    {"user_id": 1, "name": "Виноградов Максим"...},
    {"user_id": 2, "name": "Антон Чехов"...},
    {"user_id": 3, "name": "Александр Пушкин"...},
    {"user_id": 4, "name": "Сергей Артамонов"...},
]
'''