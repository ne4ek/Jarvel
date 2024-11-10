from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from application.messages.custom_errors.duration_error import DurationTooLongError
from application.messages.services.message_service import TelegramMessageService
from application.messages.message_transcriber import audio_to_text_converter
from icecream import ic
from aiogram.exceptions import TelegramBadRequest

class ProcessMessageHandlers:
    def __init__(self, message_service: TelegramMessageService):
        self.message_service = message_service
        
    def get_router(self):
        router = Router()
        self.register_handlers(router)
        return router

    def register_handlers(self, router: Router):
        router.message(F.chat.type != "private", F.text.lower().contains("ctrl"))(self.ctrl_message_handler)
        router.message(F.chat.type != "private")(self.message_handler)

    async def ctrl_message_handler(self, message: types.Message):
        #TODO: Доделать обработку ctrl
        ic("ctrl_message_handler", message)
        if message.forward_from:
            return
        text = message.text
        if message.reply_to_message:
            replyed_message = message.reply_to_message
            text = f"@{replyed_message.from_user.username}  {replyed_message.text} {text}"
        bot = await message.bot.get_me()
        bot_username = bot.username
        sender_username = "@" + message.from_user.username
        message_id = message.message_id
        chat_id = message.chat.id
        ctrl_result = await self.message_service.process_ctrl(message_id, chat_id, text, bot_username, sender_username)
        
        if not ctrl_result:
            return
        await message.reply(ctrl_result)

    @audio_to_text_converter
    async def message_handler(self, message: types.Message, state: FSMContext):
        
        bot = message.bot
        if message.text:
            await self.message_service.save_message(message)
            if message.reply_to_message and message.reply_to_message.from_user.id == bot.id and "Расшифрованное сообщение:" in message.reply_to_message.text:
                return
            if not (self.message_service.is_bot_mentioned(message.text) or (message.reply_to_message and message.reply_to_message.from_user.id == message.bot.id)):
                return
            bot_message = await message.reply(text="Обрабатываю запрос...")
            response: dict = await self.message_service.call_assistant(bot_message, message, state)
            # ic(response)
            try:
                if response:
                    parse_mode = response.get("parse_mode") if "parse_mode" in response.keys() else ParseMode.HTML
                else:
                    parse_mode = ParseMode.HTML
                bot_message = await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"), parse_mode=parse_mode)
                await self.message_service.save_message(bot_message)
            except TelegramBadRequest as tbr:
                # ic(str(tbr))
                await bot_message.edit_text(text="Ошибка обработки сообщения")
                raise tbr     
            except Exception as e:
                await bot_message.edit_text(text="Ошибка обработки сообщения")
                ic(str(e))

                
