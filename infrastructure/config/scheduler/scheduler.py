from apscheduler.schedulers.asyncio import AsyncIOScheduler
from application.scheduler.services.scheduler_service import SchedulerService
import pytz


scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
scheduler_service = SchedulerService(scheduler)