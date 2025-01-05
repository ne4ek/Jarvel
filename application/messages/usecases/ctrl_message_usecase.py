from typing import Union
import re
from datetime import datetime, timedelta
import pytz
from domain.entities.ctrl_message import CtrlMessage
from application.messages.services.ctrl_job_service import CtrlJobService
from application.providers.repositories_provider import RepositoriesDependencyProvider
from icecream import ic
class CtrlMessageUseCase:
    def __init__(self, ctrl_job_service: CtrlJobService, repositories_provider: RepositoriesDependencyProvider):
        self.ctrl_job_service = ctrl_job_service
        self.ctrls_rep = repositories_provider.get_ctrls_repository()

    async def execute(self, text: str, message_id: int, chat_id: int, bot_username: str, sender_username: str):
        w, d, h, m = 0, 0, 0, 0
        _mentioned_users = re.findall(r"@\w+", text)
        mentioned_users = []
        for user in _mentioned_users:
            if user != '@' + bot_username and user not in mentioned_users:
                mentioned_users.append(user)

        ctrl_text = re.search(r"ctrl (.*)", text.lower())
        ic(ctrl_text)
        ctrl_text = ctrl_text.group(1) if ctrl_text else "24"
        ic(ctrl_text)
        if ctrl_text != "24":
            # find number associated with "w" (weeks)
            w = re.findall(r"(\d+)w", ctrl_text)
            w = int(w[0]) if w else 0
            # find number associated with "d" (days)
            d = re.findall(r"(\d+)d", ctrl_text)
            d = int(d[0]) if d else 0
            # find number associated with "h" (hours)
            h = re.findall(r"(\d+)h", ctrl_text)
            h = int(h[0]) if h else 0
            # find number associated with "m" (minutes)
            m = re.findall(r"(\d+)m", ctrl_text)
            m = int(m[0]) if m else 0
        # if no tags were found
        if not any([w, d, h, m]):
            h = re.findall(r"\d+", ctrl_text)
            h = int(h[0]) if h else 24
        if m > 59:
            h += m // 60
            m = m % 60
        if h > 23:
            d += h // 24
            h %= 24
            
        run_at = datetime.now(tz=pytz.timezone("Europe/Moscow")) + timedelta(weeks=w,
                                                                                days=d,
                                                                                hours=h,
                                                                                minutes=m)
        reply_text = "Сообщение принято на контроль!\nЯ напомню о нём "
        if w == d == 0:
            if h > 0 or m > 0:
                reply_text += "через "
            if h > 0:
                if h in [1, 21]:
                    reply_text += f"{h} час"
                elif h in [2, 3, 4, 22, 23, 24]:
                    reply_text += f"{h} часа"
                else:
                    reply_text += f"{h} часов"
                if m > 0:
                    reply_text += " и "
            if m > 0:
                if m in [1, 21, 31, 41, 51]:
                    reply_text += f"{m} минуту"
                elif m in [2, 3, 4, 22, 23, 24, 32, 33, 34, 42, 43, 44, 52, 53, 54]:
                    reply_text += f"{m} минуты"
                else:
                    reply_text += f"{m} минут"
        else:
            ctrl_date = run_at.strftime("%d.%m")
            ctrl_time = run_at.strftime("%H:%M")
            reply_text += f"{ctrl_date} в {ctrl_time}"
        
        ctrl_message = CtrlMessage(run_date=run_at,
                                   chat_id=chat_id,
                                   ctrl_usernames=" ".join(mentioned_users),
                                   reply_message_id=message_id,
                                   fyi_usernames=sender_username)
        await self.ctrls_rep.save(ctrl_message)
        self.ctrl_job_service.add_saved_ctrl_job(ctrl_message)
        return reply_text
        