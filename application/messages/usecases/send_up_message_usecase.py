from aiogram import Bot
from domain.entities.up_message import UpMessage
from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from domain.entities.job import Job
from infrastructure.config.scheduler.scheduler import scheduler_service
from datetime import timedelta
from random import choice
from icecream import ic

class SendUpUseCase:
    def __init__(self, bot: Bot, repositories: RepositoriesDependencyProviderImplAsync):
        self.bot = bot
        self.repositories = repositories
        self.ups_repository = repositories.get_ups_repository()
        
    async def execute(self, up_message: UpMessage):       
        if self.__interval_is_less_week(up_message=up_message):
            text = f"АП @{up_message.up_username}"
            await self.__reload_job_double_interval(up_message=up_message)
        else:
            phrases = ["Какой статус?", "Какой статус у задачи?", "Как дела с этим?", "Как дела?"]
            text = f"@{up_message.up_username}\n\n{choice(phrases)}"
            await self.__reload_job_from_start(up_message=up_message)
        await self.bot.send_message(chat_id=up_message.chat_id,
                                    reply_to_message_id=up_message.bot_message_id,
                                    text=text)
    def __interval_is_less_week(self, up_message: UpMessage) -> bool:
        difference = abs(up_message.next_up_date - up_message.present_date)
        return difference < timedelta(weeks=1)
            
    
    async def __reload_job_double_interval(self, up_message: UpMessage):
        new_interval = up_message.interval * 2
        await self.__reload_job(new_interval=new_interval, up_message=up_message)
        
    async def __reload_job_from_start(self, up_message: UpMessage):
        new_interval = up_message.starting_interval
        await self.__reload_job(new_interval=new_interval, up_message=up_message)

        
    async def __reload_job(self, new_interval, up_message: UpMessage):
        new_next_up_date = up_message.next_up_date + new_interval
        new_present_date = up_message.next_up_date
        
        up_message.interval = new_interval
        up_message.next_up_date = new_next_up_date
        up_message.present_date = new_present_date
        await self.ups_repository.update_time(up_message=up_message)
        job = Job(func=self.execute, trigger="date", run_date=up_message.next_up_date, job_id=up_message.up_message_id ,args=[up_message])
        scheduler_service.add_job(job)
        