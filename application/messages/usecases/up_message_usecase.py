from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from domain.entities.up_message import UpMessage
from application.messages.services.up_job_service import UpJobService
from aiogram.types import Message
from icecream import ic
import re
from datetime import datetime, timedelta
import pytz

class UpMessageUseCase:
    def __init__(self, up_job_service: UpJobService, repositories_provider: RepositoriesDependencyProviderImplAsync):
        self.up_job_service = up_job_service
        self.repositories_provider = repositories_provider
        self.up_repository = repositories_provider.get_ups_repository()

    async def execute(self, message: Message):
        w, d, h, m = 0, 0, 0, 0
        text: str = message.text.strip()
        _up_usernames = re.findall(r"@\w+", text)

        up_text = re.search(r"ап (.*)", text.lower())
        up_text = up_text.group(1) if up_text else "24"

        up_usernames = []
        for up_username in _up_usernames:
            up_usernames.append(up_username.replace("@", ""))
        
        bot_user = await message.bot.get_me()
        bot_name = bot_user.username
        
        if bot_name in up_usernames:        
            await message.reply("Меня нельзя апать.")
            up_usernames.remove(bot_name)
        if not up_usernames:
            return

        if up_text != "24":
            w = re.findall(r"(\d+)w", up_text)
            w = int(w[0]) if w else 0
            d = re.findall(r"(\d+)d", up_text)
            d = int(d[0]) if d else 0
            h = re.findall(r"(\d+)h", up_text)
            h = int(h[0]) if h else 0
            m = re.findall(r"(\d+)m", up_text)
            m = int(m[0]) if m else 0
        if not any([w, d, h, m]):
            h = re.findall(r"\d+", up_text)
            h = int(h[0]) if h else 24

        if m > 59:
            h += m // 60
            m = m % 60
        if h > 23:
            d += h // 24
            h %= 24
            
        start_date = datetime.now(tz=pytz.timezone("Europe/Moscow"))
        interval = timedelta(weeks=w, days=d, hours=h, minutes=m)
        next_up_date = start_date + interval

        
        up_message = UpMessage(start_date=start_date,
                               next_up_date=next_up_date,
                               interval=interval,
                               starting_interval=interval,
                               reply_message_id=message.message_id,
                               fyi_username=message.from_user.username,
                               chat_id=message.chat.id,
                               present_date=start_date,       
                               )

        for up_username in up_usernames:
            if not await self.up_repository.get_up_by_username_and_chat_id(username=up_username, chat_id=message.chat.id):         
                up_id = await self.__save_up_message(up_message, up_username) 
                bot_message = await message.reply(f"@{up_username} поставлен на апание.")
                up_message.bot_message_id = bot_message.message_id
                await self.up_repository.add_bot_id_by_up_id(bot_message_id=bot_message.message_id, up_id=up_id)
            else:
                await message.reply(f"@{up_username} уже апаеться.")
    
    
    async def __save_up_message(self, up_message: UpMessage, up_username):
        up_message.up_username = up_username
        up_id = await self.up_repository.save(up_message=up_message)
        up_message.up_message_id = up_id
        self.up_job_service.add_saved_up_job(up_message)
        return up_id
        
        
    async def execute_ready_up(self, message: Message):
        up_repository = self.repositories_provider.get_ups_repository()
        up_message_from_db = await up_repository.get_up_by_username_and_chat_id(message.from_user.username, message.chat.id)
        if not up_message_from_db:
            return 
        await up_repository.deactivate_up(up_message_from_db.up_message_id)
        self.up_job_service.remove_job_by_id(up_message_from_db.up_message_id)
        text = f"@{up_message_from_db.up_username} выполнил задачу\n\n@{up_message_from_db.fyi_username} FYI"
        return text