from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from application.tasks.services.tunneling_service import TunnelingService
from aiogram.fsm.state import StatesGroup, State
from domain.entities.tunneling_message import TunnelingMessage
from aiogram.exceptions import TelegramBadRequest
from icecream import ic
class TunnelingState(StatesGroup):
    waiting_for_source_chat = State()
    waiting_for_destination_chat = State()

class TunnelingMenuHandlers:
    def __init__(self, tunneling_service: TunnelingService):
        self.tunneling_service = tunneling_service


    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_state(router)
        return router
    
    
    def __register_callbacks(self, router: Router):
        router.callback_query.register(self.tunneling_menu_start_callback, F.data == "user_go_to tunneling_menu")
        router.callback_query.register(self.create_one_way_tunnel_callback, F.data == "create_one_way_tunnel")
        router.callback_query.register(self.create_two_way_tunnel_callback, F.data == "create_two_way_tunnel")
        router.callback_query.register(self.stop_tunnel_callback, F.data == "stop_tunnel")
        router.callback_query.register(self.my_tunnels_callback, F.data == "my_tunnels")
        router.callback_query.register(self.tunneling_confirm_send_notification_callback, F.data.startswith("tunnel_notify"))
    
    def __register_state(self, router: Router):
        router.message(TunnelingState.waiting_for_source_chat)(self.waiting_for_source_chat)
        router.message(TunnelingState.waiting_for_destination_chat)(self.waiting_for_destination_chat)
        router.message(TunnelingState.send_notification)(self.send_notification)
        return router   

    async def tunneling_menu_start_callback(self, callback: CallbackQuery):
        await callback.message.answer(reply_markup=self.tunneling_service.get_tunneling_menu_keyboard(callback.from_user.id))

    async def create_one_way_tunnel_callback(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.answer("Отправьте ссылку на чат, из которого будет отправляться сообщение")
        tunneling_message = TunnelingMessage(
            tunnel_type="one_way",
            user_id=callback.from_user.id
        )
        await state.update_data(tunneling_message=tunneling_message)
        await state.update_data(text="Отправьте ссылку на чат, в который будет отправляться сообщение")
        await state.set_state(TunnelingState.waiting_for_source_chat)
    

    async def create_two_way_tunnel_callback(self, callback: CallbackQuery, state: FSMContext):
        await callback.message.answer("Отправьте ссылку на первый чат")
        tunneling_message = TunnelingMessage(
            tunnel_type="two_way",
            user_id=callback.from_user.id
        )
        await state.update_data(tunneling_message=tunneling_message)
        await state.update_data(text="Отправьте ссылку на второй чат")
        await state.set_state(TunnelingState.waiting_for_source_chat)

    async def waiting_for_source_chat(self, message: Message, state: FSMContext):
        if self.tunneling_service.is_telegram_link(message.text):
            chat_id, topic_id = self.tunneling_service.get_chat_topik_id_from_link(message.text)
            tunneling_message = await state.get_data("tunneling_message")
            tunneling_message.from_chat_id = chat_id
            tunneling_message.from_topic_id = topic_id
            await state.update_data(tunneling_message=tunneling_message)
            await message.answer(await state.get_data("text"))
            await state.set_state(TunnelingState.waiting_for_destination_chat)
        else:
            await message.answer("Это не выглядит как ссылка на чат, попробуйте еще раз")
    
    async def waiting_for_destination_chat(self, message: Message, state: FSMContext):
        if self.tunneling_service.is_telegram_link(message.text):
            tunneling_message = await state.get_data("tunneling_message")
            tunneling_message.to_chat_id, tunneling_message.to_topic_id = self.tunneling_service.get_chat_topik_id_from_link(message.text)
            await state.update_data(tunneling_message=tunneling_message)
            if await self.tunneling_service.is_tunnel_already_exists(tunneling_message):
                await message.answer("Такой туннель уже существует")
                await state.clear()
                return
            await self.tunneling_service.create_tunnel(tunneling_message)
            await message.answer(self.tunneling_service.get_response_for_confirm_notification(tunneling_message)["text"], 
                                 reply_markup=self.tunneling_service.get_response_for_confirm_notification(tunneling_message)["keyboard"])
            await state.clear()
        else:
            await message.answer("Это не выглядит как ссылка на чат, попробуйте еще раз")
    
    async def tunneling_confirm_send_notification_callback(self, callback: CallbackQuery):
        tunneling_id = callback.data.split()[-1]
        tunneling_message = await self.tunneling_service.get_tunnel_by_id(tunneling_id)
        bot = callback.bot
        if tunneling_message.tunnel_type == "one_way":
            text_for_source_chat = f'echo "HI tunnel started... successfully..." 🫡.\To {self.tunneling_service.get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)}'
            text_for_destination_chat = f'echo "HI tunnel started... successfully..." 🫡.\nFrom {self.tunneling_service.get_telegram_link(tunneling_message.to_chat_id, tunneling_message.to_topic_id)}'
            source_message_id = await self.__send_message_to_chat(bot, text_for_source_chat, tunneling_message.from_chat_id, tunneling_message.from_topic_id)
            destination_message_id = await self.__send_message_to_chat(bot, text_for_destination_chat, tunneling_message.to_chat_id, tunneling_message.to_topic_id)
        else:
            text = ""


    async def __send_message_to_chat(self, bot: Bot, text: str, chat_id: int, message_thread_id: int):
        try:
            sended_message = await bot.send_message(chat_id=chat_id, text=text, message_thread_id=message_thread_id)
        except TelegramBadRequest as tbr:
            ic(str(tbr))
            return None
        else:
            try:
                await bot.pin_chat_message(chat_id=chat_id, message_id=sended_message.message_id)
            except TelegramBadRequest:
                ic(str(tbr))
                return None
            return sended_message.message_id