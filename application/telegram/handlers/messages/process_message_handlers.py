from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from application.messages.custom_errors.duration_error import DurationTooLongError
from application.messages.services.message_service import TelegramMessageService
from application.messages.message_transcriber import audio_to_text_converter
from icecream import ic
from aiogram.exceptions import TelegramBadRequest
import re
from const import MIN_MESSAGE_LENGTH_FOR_SHORTENING

class ProcessMessageHandlers:
    def __init__(self, message_service: TelegramMessageService):
        self.message_service = message_service
        
    def get_router(self):
        router = Router()
        self.register_handlers(router)
        return router

    def register_handlers(self, router: Router):
        router.message(F.chat.type != "private", F.func(self.contains_ctrl_in_words))(self.ctrl_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_up_in_words))(self.up_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_vipolnil_in_words))(self.up_ready_handler)
        router.message(F.chat.type != "private")(self.message_handler)

    def contains_up_in_words(self, message: types.Message) -> bool:
        pattern = re.compile(r'\bап\b.*(?:@\w+)+', re.IGNORECASE)
        if not message.text:
            return False
        return  bool(pattern.search(message.text))
    
    def contains_ctrl_in_words(self, message: types.Message) -> bool:
        if not message.text:
            return False
        words = message.text.lower().split()
        return "ctrl" in words
    
    def contains_vipolnil_in_words(self, message: types.Message) -> bool:
        if not message.text:
            return False
        words = message.text.lower().split()
        return "выполнил" in words
    
    
    async def ctrl_message_handler(self, message: types.Message):
        ic("ctrl_message_handler")
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
        message_text = message.text or message.caption
        if message_text:
            await self.message_service.save_message(message)
            # if message.reply_to_message and message.reply_to_message.from_user.id == message.bot.id:
            #     return 
            if not self.message_service.is_bot_mentioned(message_text):
                # if len(message_text) > MIN_MESSAGE_LENGTH_FOR_SHORTENING:  
                #         bot_message = await message.reply(text="Сокращаю...")
                #         shorten_message = await self.message_service.shorten_text(message_text)
                #         ic(shorten_message)
                #         await bot_message.edit_text(shorten_message)
                #         return
                return
                
            bot_message = await message.reply(text="Обрабатываю запрос...")
            response: dict = await self.message_service.call_assistant(bot_message, message, state)
            ic(response)
            try:
                if response:
                    parse_mode = response.get("parse_mode") if "parse_mode" in response.keys() else ParseMode.HTML
                else:
                    parse_mode = ParseMode.HTML
                ic(parse_mode)
                bot_message = await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"), parse_mode=parse_mode)
                await self.message_service.save_message(bot_message)
            except TelegramBadRequest as tbr:
                await bot_message.edit_text(text="Ошибка обработки сообщения")
                raise tbr     
            except Exception as e:
                await bot_message.edit_text(text="Ошибка обработки сообщения")
                ic(str(e))

    async def up_message_handler(self, message: types.Message):
        ic("up_message_handler")
        up_result = await self.message_service.process_up(message)
        if up_result:
            await message.reply(up_result)
        
    async def up_ready_handler(self, message: types.Message):
        ic("up_ready_handler")
        up_ready_result = await self.message_service.process_ready_up(message)
        ic(up_ready_result)
        if up_ready_result:
            await message.reply(up_ready_result)

                
