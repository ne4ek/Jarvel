from domain.entities.tunneling_message import TunnelingMessage
from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import re
from icecream import ic
class TunnelingService:
    def __init__(self, repository_provider: RepositoriesDependencyProviderImplAsync):
        self.repository_provider = repository_provider
        self.tunneling_repository = repository_provider.get_tunneling_repository()
        self.users_repository = repository_provider.get_users_repository()
        
    async def create_tunnel(self, tunneling_message: TunnelingMessage) -> tuple[int]:
        if tunneling_message.tunnel_type == "one_way":
            tunneling_id = await self.tunneling_repository.save(tunneling_message)
            return (tunneling_id,)
        elif tunneling_message.tunnel_type == "two_way":
            tunneling_id = await self.tunneling_repository.save(tunneling_message)
            tunneling_message_2 = TunnelingMessage(
                tunnel_type="two_way",
                from_chat_id=tunneling_message.to_chat_id,
                from_topic_id=tunneling_message.to_topic_id,
                to_chat_id=tunneling_message.from_chat_id,
                to_topic_id=tunneling_message.from_topic_id,
                user_id=tunneling_message.user_id,
                company_id=tunneling_message.company_id,
                specify_chat_pinned_message_id=tunneling_message.source_chat_pinned_message_id,
                source_chat_pinned_message_id=tunneling_message.specify_chat_pinned_message_id
            )
            tunneling_id_2 = await self.tunneling_repository.save(tunneling_message_2)
            return (tunneling_id, tunneling_id_2)
        else:
            ic(f"Неизвестный тип туннеля: {tunneling_message.tunnel_type}")
        

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
        

    def get_tunneling_menu_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Создать односторонний туннель", callback_data="create_one_way_tunnel")],
                [InlineKeyboardButton(text="Создать зеркальный туннель", callback_data="create_two_way_tunnel")],
                [InlineKeyboardButton(text="Мои туннели", callback_data="my_tunnels")],
                [InlineKeyboardButton(text="Главное меню", callback_data="user_go_to main_menu")]
            ]
        )
        return keyboard

    def get_response_for_confirm_notification(self, tunneling_message: TunnelingMessage) -> dict:
        text = ""
        if tunneling_message.tunnel_type == "one_way":
            text = f"✅ Туннель создан! Сообщения из {self.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)} будут пересылаться в {self.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)}."
            if isinstance(tunneling_message.tunneling_id, tuple):
                tunneling_id = tunneling_message.tunneling_id[0]
            else:
                tunneling_id = tunneling_message.tunneling_id
        else:
            text = f"✅ Туннель создан! Сообщения из {self.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)} и {self.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)} будут пересылаться друг в друга."
            tunneling_id = f"{tunneling_message.tunneling_id[0]}_{tunneling_message.tunneling_id[1]}"
        base_keyboard = self.get_response_base_for_tunnel_menu(text)["keyboard"]
        text += "\n\nОтправить уведомления в чаты?"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Да", callback_data=f"tunnel_notify {tunneling_id}")],
                [InlineKeyboardButton(text="Нет", callback_data="user_go_to tunneling_menu")],
            ]
        )
        keyboard.inline_keyboard.extend(base_keyboard.inline_keyboard)
        return {"text": text, "keyboard": keyboard}
    

    async def is_tunnel_already_exists(self, tunneling_message: TunnelingMessage) -> bool:
        return await self.tunneling_repository.get_any_by_full_info(tunneling_message) is not None  

    async def get_tunnel_by_from_info(self, tunneling_message: TunnelingMessage) -> TunnelingMessage:
        
        return await self.tunneling_repository.get_any_by_from_info(tunneling_message)

    def get_response_base_for_tunnel_menu(self, text: str="") -> dict:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Меню туннелей", callback_data="user_go_to tunneling_menu")],
                [InlineKeyboardButton(text="Главное меню", callback_data="user_go_to main_menu")],
            ]
        )
        return {"text": text, "keyboard": keyboard}


    async def get_tunnel_by_id(self, tunneling_id: int | str) -> TunnelingMessage:
        return await self.tunneling_repository.get_by_id(int(tunneling_id))

    async def update_pinned_message_ids_by_tunneling_id(self, tunneling_message: TunnelingMessage) -> None:
        if tunneling_message.tunnel_type == "one_way":
            await self.tunneling_repository.update_pinned_message_ids_by_tunneling_id(tunneling_message)
        elif tunneling_message.tunnel_type == "two_way":
            tunneling_message_2 = TunnelingMessage(
                tunnel_type="two_way",
                from_chat_id=tunneling_message.to_chat_id,
                from_topic_id=tunneling_message.to_topic_id,
                to_chat_id=tunneling_message.from_chat_id,
                to_topic_id=tunneling_message.from_topic_id,
            )
            await self.tunneling_repository.update_pinned_message_ids_by_tunneling_id(tunneling_message)
            await self.tunneling_repository.update_pinned_message_ids_by_tunneling_id(tunneling_message_2)


    async def get_my_tunnels_full_response(self, user_id: int) -> dict:
        tunnels = await self.tunneling_repository.get_all_by_user_id(user_id)
        text = "Ваши туннели:" if tunnels else "У вас нет туннелей"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        already_in_keyboard = []
        for tunnel in tunnels:
            if tunnel.tunnel_type == "one_way":
                keyboard.inline_keyboard.append([InlineKeyboardButton(text=f"{self.get_telegram_link(tunnel.from_chat_id, tunnel.from_topic_id)} -> {self.get_telegram_link(tunnel.to_chat_id, tunnel.to_topic_id)}", callback_data=f"get_tunnel_info {tunnel.tunneling_id}")])
            elif tunnel.tunnel_type == "two_way" :
                if f"{tunnel.from_chat_id}_{tunnel.from_topic_id}_{tunnel.to_chat_id}_{tunnel.to_topic_id}" not in already_in_keyboard:
                    already_in_keyboard.append(f"{tunnel.from_chat_id}_{tunnel.from_topic_id}_{tunnel.to_chat_id}_{tunnel.to_topic_id}")
                    already_in_keyboard.append(f"{tunnel.to_chat_id}_{tunnel.to_topic_id}_{tunnel.from_chat_id}_{tunnel.from_topic_id}")
                    keyboard.inline_keyboard.append([InlineKeyboardButton(text=f"{self.get_telegram_link(tunnel.from_chat_id, tunnel.from_topic_id)} <-> {self.get_telegram_link(tunnel.to_chat_id, tunnel.to_topic_id)}", callback_data=f"get_tunnel_info {tunnel.tunneling_id}")])
        base_keyboard = self.get_response_base_for_tunnel_menu()["keyboard"]
        keyboard.inline_keyboard.extend(base_keyboard.inline_keyboard)
        return {"text": text, "keyboard": keyboard}


    async def get_tunnel_info_full_response(self, tunneling_id: int | str) -> dict:
        tunneling_message = await self.get_tunnel_by_id(tunneling_id)
        slug = "->" if tunneling_message.tunnel_type == "one_way" else "<->"
        user = await self.users_repository.get_by_id(tunneling_message.user_id)
        creator_text = f"Создатель:  {user.username}\n" if user and user.username else ""
        status_text = "Активный" if tunneling_message.is_active else "Неактивный"
        text = f"Туннель {self.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)} {slug} {self.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)}\n\n{creator_text}Статус: {status_text}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        if tunneling_message.is_active:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="Остановить туннель", callback_data=f"stop_tunnel {tunneling_message.tunneling_id}")])
        else:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="Восстановить туннель", callback_data=f"start_tunnel {tunneling_message.tunneling_id}")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Удалить туннель", callback_data=f"delete_tunnel {tunneling_message.tunneling_id}")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data=f"my_tunnels")])
        base_keyboard = self.get_response_base_for_tunnel_menu()["keyboard"]
        keyboard.inline_keyboard.extend(base_keyboard.inline_keyboard)
        return {"text": text, "keyboard": keyboard}
    
    async def get_confirm_delete_full_response(self, tunneling_id: int) -> dict:
        tunneling_message = await self.get_tunnel_by_id(tunneling_id)
        slug = "->" if tunneling_message.tunnel_type == "one_way" else "<->"
        text = f"Вы уверены, что хотите удалить туннель {self.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)} {slug} {self.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)}?\n\nЭто действие нельзя будет отменить!"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Да", callback_data=f"confirm_delete_tunnel {tunneling_message.tunneling_id}")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Нет", callback_data=f"get_tunnel_info {tunneling_message.tunneling_id}")])
        base_keyboard = self.get_response_base_for_tunnel_menu()["keyboard"]
        keyboard.inline_keyboard.extend(base_keyboard.inline_keyboard)
        return {"text": text, "keyboard": keyboard}
    

    async def start_tunnel(self, tunneling_id: int) -> None:
        tunneling_message = await self.get_tunnel_by_id(tunneling_id)
        if tunneling_message.tunnel_type == "one_way":
            await self.tunneling_repository.update_is_active_by_full_info(tunneling_message, True)
        elif tunneling_message.tunnel_type == "two_way":
            second_tunneling_message = await self.tunneling_repository.get_any_by_full_info(self.__get_second_tunnel_in_two_way_tunnel(tunneling_message))
            await self.tunneling_repository.update_is_active_by_full_info(tunneling_message, True)
            await self.tunneling_repository.update_is_active_by_full_info(second_tunneling_message, True)

    async def stop_tunnel(self, tunneling_id: int) -> None:
        tunneling_message = await self.get_tunnel_by_id(tunneling_id)
        if tunneling_message.tunnel_type == "one_way":
            await self.tunneling_repository.update_is_active_by_full_info(tunneling_message, False)
        elif tunneling_message.tunnel_type == "two_way":
            second_tunneling_message = await self.tunneling_repository.get_any_by_full_info(self.__get_second_tunnel_in_two_way_tunnel(tunneling_message))
            await self.tunneling_repository.update_is_active_by_full_info(tunneling_message, False)
            await self.tunneling_repository.update_is_active_by_full_info(second_tunneling_message, False)

    async def delete_tunnel(self, tunneling_id: int) -> None:
        tunneling_message = await self.get_tunnel_by_id(tunneling_id)
        if tunneling_message.tunnel_type == "one_way":
            await self.tunneling_repository.delete_by_full_info(tunneling_message)
        elif tunneling_message.tunnel_type == "two_way":
            second_tunneling_message = await self.tunneling_repository.get_any_by_full_info(self.__get_second_tunnel_in_two_way_tunnel(tunneling_message))
            await self.tunneling_repository.delete_by_full_info(tunneling_message)
            await self.tunneling_repository.delete_by_full_info(second_tunneling_message)
    

    def __get_second_tunnel_in_two_way_tunnel(self, tunneling_message: TunnelingMessage) -> TunnelingMessage:
        return TunnelingMessage(
            tunnel_type="two_way",
            from_chat_id=tunneling_message.to_chat_id,
            from_topic_id=tunneling_message.to_topic_id,
            to_chat_id=tunneling_message.from_chat_id,
            to_topic_id=tunneling_message.from_topic_id,
        )