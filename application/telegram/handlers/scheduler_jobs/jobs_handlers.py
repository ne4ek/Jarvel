from pytz import timezone
import pytz
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

tag = "jobs_handlers"

scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))
moscow_timezone = pytz.timezone("Europe/Moscow")



def add_job_in_scheduler(func, trigger: str, run_date: datetime, args: list) -> None:
    """
    A function that adds job to the scheduler

    :param function func: Name of the function to be called by time
    :param str trigger: Type of trigger to be activated in scheduler
    :param datetime run_date: Activation time of operation
    :param list args: Arguments to be passed to func for correct function call

    :return: None
    """
    scheduler.add_job(func=func, trigger=trigger, run_date=run_date, args=args)
