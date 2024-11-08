import logging
from aiogram.types import Update
from dotenv import load_dotenv
import os


load_dotenv()
system_logger = logging.getLogger("system_logging")
user_logger = logging.getLogger("user_logging")
error_logger = logging.getLogger("error_logging")


def set_func(function: str, status: str = "info"):
    """
    Функция сохраняет лог о вызове функции

    :param str function: Название функции
    :param str status: Тип лога

    :return: None
    """
    result = f"Called Function:({function})"
    if status == "info":
        system_logger.info(result)
    elif status == "debug":
        system_logger.debug(result)


def set_inside_func(function: str, data: str, status: str = "info"):
    """
    Функция выводит информацию о логе внутри конкретной функции

    :param str function: Название функции
    :param str data: Информация, которую нужно сохранить
    :param str status: Тип лога

    :return: None
    """
    # result = f"[{tag}] [{function}]: {data}"
    result = f"[{function}]: {data}"
    if status == "info":
        system_logger.info(result)
    elif status == "debug":
        system_logger.debug(result)
    elif status == "error":
        system_logger.error(result)


def set_func_and_person(function, message, status="info"):
    """
    Функция сохраняет лог о вызове функции и о том, кто её вызвал

    :param str function: Название функции
    :param Message message: Object represents a message from telegram
    :param str status: Название функции

    :return: None
    """
    # result = f"User: {message.chat.username}/{message.chat.id} Tag: [{tag}]  Function: ({function})"
    result = f"User: {message.chat.username}/{message.chat.id} Function: ({function})"
    if status == "info":
        user_logger.info(result)
        system_logger.info(result)
    elif status == "debug":
        user_logger.debug(result)
        system_logger.debug(result)


def send_log(message):
    """
    Функция выводит сообщение пользователя отправленное без команды

    :param Message message: Object represents a message from telegram

    :return: None
    """
    result = f'User: {message.chat.username}/{message.chat.id} Send Message: "{message.text}"'
    user_logger.info(result)
    system_logger.debug(result)


def add_or_delete_user(message, command):
    """
    Функция выводит сообщение о добавлении или удалении пользователя из бд

    :param Message message: Object represents a message from telegram
    :param str command: Команда удалить или сохранить пользователя

    :return: None
    """
    if command == "add":
        result = f"Add User: {message.chat.username}/{message.chat.id}"
    else:
        result = f"Delete User: {message.chat.username}/{message.chat.id}"

    user_logger.info(result)
    system_logger.info(result)


async def error_aio_handler(update: Update):
    """
    Функция для обработки и логирования всех необработанных исключений.
    """
    error_logger.error(update.exception)
    system_logger.error(update.exception)
    # icecream.ic(update.exception)
    # icecream.ic(update)



def logs_settings():
    """
    Функция первичной настройки логов

    :return: None
    """
    # Максимально подробный вывод логов
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

    # Нормальный вывод логов
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(asctime)s - %(message)s", datefmt="%d.%m-%H:%M"
    )

    # Настройка вывода данных в файлы
    for file_path in ["logs/system_data.log", "logs/system_data.log", "logs/user_data.log"]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                pass
    
    system_handler = logging.FileHandler("logs/system_data.log")
    system_handler.setFormatter(formatter)

    user_handler = logging.FileHandler("logs/user_data.log")
    user_handler.setFormatter(formatter)

    error_handler = logging.FileHandler("logs/error_data.log")
    error_handler.setFormatter(formatter)

    global system_logger
    if os.getenv("DEVICE") == "Laptop" or os.getenv("DEVICE") == "Ubuntu":
        logging.basicConfig(
            format="[%(levelname)s] %(asctime)s - %(message)s",
            datefmt="%d.%m-%H:%M",
        )
        system_logger.setLevel(logging.DEBUG)
    else:
        system_logger.setLevel(logging.INFO)
        global error_logger
        error_logger.setLevel(logging.ERROR)
        error_logger.addHandler(error_handler)

        # from infrastructure.telegram.utils.registration_dispatcher import dp
        # dp.errors.register(error_aio_handler)

    system_logger.addHandler(system_handler)

    apscheduler_logger = logging.getLogger("apscheduler")
    apscheduler_logger.setLevel(logging.DEBUG)
    apscheduler_logger.addHandler(system_handler)

    aiogram_logger = logging.getLogger("aiogram")
    aiogram_logger.setLevel(logging.DEBUG)
    aiogram_logger.addHandler(system_handler)

    global user_logger
    user_logger.setLevel(logging.DEBUG)
    user_logger.addHandler(user_handler)



    # raise RuntimeError("Test unhandled")