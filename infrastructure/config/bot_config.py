from aiogram import Bot, types
import os
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))

def get_bot_commands():
    """
    Функция передаёт телеграмму список команд для быстрого доступа из меню

    :return: None
    """

    bot_commands = [
        types.BotCommand(command="/main_menu", description="Открыть главное меню"),
        types.BotCommand(command="/add_chat_to_company", description="Добавить групповой чат в компанию"),
        types.BotCommand(command="/registration", description="Регистрация в боте"),
        types.BotCommand(command="/tunnel", description="Создает туннель между чатами"),
        types.BotCommand(command="/stop_tunnel", description="Удаляет туннель из указанного чата"),
        types.BotCommand(command="/send", description="Отправить сообщение без форварда"),
        types.BotCommand(command="/send_f", description="Отправить сообщение с форвардом")        
       
    ]
    return bot_commands
