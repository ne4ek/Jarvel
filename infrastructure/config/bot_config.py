from aiogram import Bot, types
import os
from dotenv import load_dotenv
load_dotenv()
print(os.getenv("BOT_TOKEN"))
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
        types.BotCommand(command="/tunnel", description="tunnel"),
    ]
    return bot_commands
