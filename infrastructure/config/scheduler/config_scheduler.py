from .scheduler import scheduler
from .mailing_job_service import mail_job_service
from .ctrls_job_service import ctrl_job_service
from .meeting_job_service import meeting_job_service
from .task_job_service import task_job_service
from .ups_job_service import up_job_service

async def config():
    scheduler.start()
    await task_job_service.add_all_jobs()
    await meeting_job_service.add_all_jobs()
    await ctrl_job_service.add_all_jobs()
    await up_job_service.add_all_jobs()
    # mail_job_service.add_all_jobs()
