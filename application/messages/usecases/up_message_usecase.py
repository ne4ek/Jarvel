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
        text: str = message.text

        match = re.search(r"(?i)ап ((?:@\w+\s*)+) (\d+[wdhms])?", text)
        if not match:
            return "Неверный формат команды. Используйте: ап @nickname 1h (или другой временной интервал)."

        up_usernames = match.group(1)
        time_text = match.group(2)

        up_usernames = up_usernames.replace("@", "").split()

        bot_user = await message.bot.get_me()
        bot_name = bot_user.username
        
        if bot_name in up_usernames:        
            await message.reply("Меня нельзя апать.")
            up_usernames.remove(bot_name)
        if not up_usernames:
            return

        w = int(re.findall(r"(\d+)w", time_text)[0]) if "w" in time_text else 0
        d = int(re.findall(r"(\d+)d", time_text)[0]) if "d" in time_text else 0
        h = int(re.findall(r"(\d+)h", time_text)[0]) if "h" in time_text else 0
        m = int(re.findall(r"(\d+)m", time_text)[0]) if "m" in time_text else 0
        s = int(re.findall(r"(\d+)s", time_text)[0]) if "s" in time_text else 0

        if s > 59:
            m += s // 60
            s = s % 60
        if m > 59:
            h += m // 60
            m = m % 60
        if h > 23:
            d += h // 24
            h %= 24

        start_date = datetime.now(tz=pytz.timezone("Europe/Moscow"))
        interval = timedelta(weeks=w, days=d, hours=h, minutes=m, seconds=s)
        next_up_date = start_date + interval

        
        up_message = UpMessage(start_date=start_date,
                               next_up_date=next_up_date,
                               interval=interval,
                               starting_interval=interval,
                               reply_message_id=message.message_id,
                               fyi_usernames=message.from_user.username,
                               chat_id=message.chat.id,
                               present_date=start_date,       
                               )

        for up_username in up_usernames:
            if not await self.up_repository.get_up_by_username_and_chat_id(username=up_username, chat_id=message.chat.id):         
                await self.__save_up_message(up_message, up_username) 
                await message.reply(f"@{up_username} поставлен на апание.")
            else:
                await message.reply(f"@{up_username} уже апаеться.")
    
    
    async def __save_up_message(self, up_message: UpMessage, up_username):
        up_message.up_usernames = up_username
        up_id = await self.up_repository.save(up_message=up_message)
        up_message.up_message_id = up_id
        self.up_job_service.add_saved_up_job(up_message)
        
        
    async def execute_ready_up(self, message: Message):
        up_repository = self.repositories_provider.get_ups_repository()
        up_message_from_db = await up_repository.get_up_by_username_and_chat_id(message.from_user.username, message.chat.id)
        if not up_message_from_db:
            return 
        await up_repository.deactivate_up(up_message_from_db.up_message_id)
        self.up_job_service.remove_job_by_id(up_message_from_db.up_message_id)
        text = f"@{up_message_from_db.fyi_usernames} выполнил @{up_message_from_db.up_usernames} задачу"
        ic(text)
        return text