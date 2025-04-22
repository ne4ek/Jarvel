from domain.entities.tunneling_message import TunnelingMessage
from application.providers.repositories_provider import RepositoriesDependencyProvider
import re
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

class TunnelingService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider):
        self.repository_provider = repository_provider
        self.tunneling_repository = repository_provider.get_tunneling_repository()

    async def create_tunnel(self, tunneling_message: TunnelingMessage):
        await self.tunneling_repository.create_tunnel(tunneling_message)


    def get_telegram_link(self, chat_id: int, topic_id: int|None) -> str:
        if topic_id is None:
            topic_id = ''
        elif topic_id == 0:
            topic_id = 1
        return f"https://t.me/c/{str(chat_id).replace('-100', '')}/{topic_id}"

    def get_chat_topik_id_from_link(self, link: str) -> tuple[str]:
        splited_link = link.split("/")
        if splited_link[-2].isdigit():
            chat_id = int("-100" + splited_link[-2])
            topic_id = int(splited_link[-1])
            if topic_id == 1:
                topic_id = 0
        else:
            if '-' in splited_link[-1] and len(splited_link[-1]) == 11:
                chat_id = int(splited_link[-1])
            else:
                chat_id = int("-100" + splited_link[-1])
            topic_id = None
        return (chat_id, topic_id)

    def get_chat_topik_id_from_message(self, message: Message) -> tuple[str]:
        chat_id = message.chat.id
        topic_id = message.message_thread_id
        return (chat_id, topic_id)
    
    def is_telegram_link(self, url: str):
        pattern = r"https://t\.me/[+\w\-_/]+"
        return re.match(pattern, url)
        

    def get_tunneling_menu_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Создать односторонний туннель", callback_data="create_one_way_tunnel")],
                [InlineKeyboardButton(text="Создать зеркальный туннель", callback_data="create_two_way_tunnel")],
                [InlineKeyboardButton(text="Отключить туннель", callback_data="stop_tunnel")],
                [InlineKeyboardButton(text="Мои туннели", callback_data="user_go_to tunneling_menu")],
                [InlineKeyboardButton(text="Главное меню", callback_data="user_go_to main_menu")]
            ]
        )
        return keyboard

    def get_response_for_confirm_notification(self, tunneling_message: TunnelingMessage) -> dict:
        text = ""
        if tunneling_message.tunnel_type == "one_way":
            text = f"✅ Туннель создан! Сообщения из {self.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)} будут пересылаться в {self.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)}."
        else:
            text = f"✅ Туннель создан! Сообщения из {self.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)} и {self.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)} будут пересылаться друг в друга."

        text += "\n\nОтправить уведомления в чаты?"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да", callback_data=f"tunnel_notify {tunneling_message.tunneling_id}")],
                [InlineKeyboardButton(text="Меню туннелей", callback_data="user_go_to tunneling_menu")],
                [InlineKeyboardButton(text="Главное меню", callback_data="user_go_to main_menu")]
            ]
        )
        return {"text": text, "keyboard": keyboard}
    

