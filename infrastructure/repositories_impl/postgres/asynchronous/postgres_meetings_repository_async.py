from datetime import datetime
from typing import List, Optional, Dict, Union
from domain.entities.meeting import Meeting
from domain.entities.unknown_user import UnknownUser
from application.repositories.meetings_repository import MeetingsRepository
from application.repositories.users_repository import UsersRepository
from application.repositories.companies_repository import CompaniesRepository
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
import json
import pytz
from icecream import ic


class PostgresMeetingsRepositoryAsync(MeetingsRepository):
    def __init__(self, db_connection_pool, users_repository: UsersRepository,
                 companies_repository: CompaniesRepository):
        self.db_connection_pool = db_connection_pool
        self.users_repository: UsersRepository = users_repository
        self.companies_repository: CompaniesRepository = companies_repository

    @open_and_close_connection
    async def save(self, meeting: Meeting, connection=None) -> int:
        sql_query = (
            "INSERT INTO public.meeting (author_id, moderator_id, known_participants_ids, topic, link, meeting_datetime, "
            "invitation_type, remind_datetime, duration, company_id, unknown_participants_data, status, created_at) "
            "VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, "
            "(SELECT company_id FROM public.company WHERE company_code = $10), $11::jsonb, $12, $13) RETURNING meeting_id;"
        )
        ic(meeting.meeting_datetime)
        sql_values = (
            meeting.author_id,
            meeting.moderator_id,
            meeting.participants_id,
            meeting.topic,
            meeting.link,
            meeting.meeting_datetime,
            meeting.invitation_type,
            meeting.remind_datetime,
            int(meeting.duration),
            meeting.company_code,
            json.dumps(meeting.unknown_participants_data),
            "pending",
            datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow')),
        )
        ic(sql_values)
        result = await connection.fetch(sql_query, *sql_values)
        return result[0]["meeting_id"]


    @open_and_close_connection
    async def get_all(self, connection=None) -> List[Meeting]:
        result = await connection.fetch("SELECT * FROM public.meeting")
        return await self._map_meetings(result)

    @open_and_close_connection
    async def get_all_meeting_ids(self, connection=None) -> List[int]:
        result = await connection.fetch("SELECT meeting_id FROM public.meeting")
        return [row['meeting_id'] for row in result]

    @open_and_close_connection
    async def get_by_user_id(self, user_id: int, connection=None) -> List[Meeting]:
        result = await connection.fetch(
            f"SELECT * FROM public.meeting WHERE moderator_id = {user_id} OR {user_id} = ANY(known_participants_ids)"
        )
        return await self._map_meetings(result)

    @open_and_close_connection
    async def get_last_n_by_user_id(self, user_id: int, n: int, connection=None) -> List[Meeting]:
        result = await connection.fetch(
            f"SELECT * FROM public.meeting WHERE moderator_id = {user_id} OR {user_id} = ANY(known_participants_ids) "
            f"ORDER BY meeting_datetime ASC LIMIT {n}"
        )
        return await self._map_meetings(result)

    @open_and_close_connection
    async def get_by_user_id_filter_deadline(self, user_id: int, deadline: datetime, connection=None) -> List[Meeting]:
        sql_request = f"SELECT * FROM public.meeting WHERE (moderator_id = {user_id} OR {user_id} = ANY(known_participants_ids)) "
        datetime_sql_part = (
            "AND meeting_datetime AT TIME ZONE 'Europe/Moscow' <= "
            "DATE_TRUNC('day', NOW()) + "
            f"INTERVAL '{deadline.days} days' + INTERVAL '{deadline.hour} hour' + INTERVAL '{deadline.minute} minutes'"
        )
        sql_request += datetime_sql_part
        sql_request += " ORDER BY meeting_datetime ASC"
        result = await connection.fetch(sql_request)
        return await self._map_meetings(result)

    @open_and_close_connection
    async def get_by_meeting_id(self, meeting_id: int, connection=None) -> Optional[Meeting]:
        query = f"SELECT * FROM public.meeting WHERE meeting_id = $1"
        result = await connection.fetch(query, meeting_id)
        if result:
            return await self._map_meeting(result[0])
        return None

    @open_and_close_connection
    async def get_by_user_id_and_company_code(self, user_id: int, company_code: str, connection=None) -> List[Meeting]:
        query = (
            f"SELECT * FROM public.meeting WHERE (moderator_id = $1 OR $1 = ANY(known_participants_ids)) "
            f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2)"
        )
        result = await connection.fetch(query, user_id, company_code)
        return await self._map_meetings(result)

    @open_and_close_connection
    async def get_by_moderator_id_and_company_code(self, moderator_id: int, company_code: str, status: str = None, connection=None) -> List[Meeting]:
        if status:
            query = (
                f"SELECT * FROM public.meeting WHERE moderator_id = $1 "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) "
                f"AND status = $3"
            )
            result = await connection.fetch(query, moderator_id, company_code, status)
        else:
            query = (
                f"SELECT * FROM public.meeting WHERE moderator_id = $1 "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2)"
            )
            result = await connection.fetch(query, moderator_id, company_code)
        return await self._map_meetings(result)

    @open_and_close_connection
    async def get_by_participant_id_and_company_code(self, participant_id: int, company_code: str, status: str = None, connection=None) -> List[Meeting]:
        if not status:
            query = (
                f"SELECT * FROM public.meeting WHERE $1 = ANY(known_participants_ids) "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2)"
            )
            result = await connection.fetch(query, participant_id, company_code)
        else:
            query = (
                f"SELECT * FROM public.meeting WHERE $1 = ANY(known_participants_ids) "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) "
                f"AND status = $3"
            )
            result = await connection.fetch(query, participant_id, company_code, status)
        return await self._map_meetings(result)

    @open_and_close_connection
    async def set_link(self, meeting_id: int, link: str, connection=None):
        query = f"UPDATE public.meeting SET link = $1 WHERE meeting_id = $2"
        await connection.fetch(query, link, meeting_id)

    @open_and_close_connection
    async def set_status(self, meeting_id: int, status: str, connection=None):
        query = f"UPDATE public.meeting SET status = $1 WHERE meeting_id = $2"
        await connection.fetch(query, status, meeting_id)

    @open_and_close_connection
    async def set_participants(self, participants_ids: list[int], meeting_id: int, connection=None):
        query = f"UPDATE public.meeting SET known_participants_ids = $1 WHERE meeting_id = $2"
        await connection.fetch(query, participants_ids, meeting_id)

    @open_and_close_connection
    async def set_meeting_datetime(self, meeting: Meeting, connection=None):
        query = f"UPDATE public.meeting SET meeting_datetime = $1, remind_datetime = $2 WHERE meeting_id = $3"
        await connection.fetch(query, meeting.meeting_datetime, meeting.remind_datetime, meeting.meeting_id)

    @open_and_close_connection
    async def get_by_status_and_company_code_and_user_id(self, status: str, user_id: int, company_code: str, connection=None) -> List[Meeting]:
        query = (
            "SELECT * FROM public.meeting WHERE ($1 = ANY(known_participants_ids) OR $1 = moderator_id) "
            "AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) "
            "AND status = $3"
        )
        result = await connection.fetch(query, user_id, company_code, status)
        return await self._map_meetings(result)

    async def _map_meetings(self, rows) -> List[Meeting]:
        meetings = []
        for row in rows:
            meeting = await self._map_meeting(row)
            meetings.append(meeting)
        return meetings

    async def _map_meeting(self, row) -> Meeting:
        meeting = Meeting(
            meeting_id=row['meeting_id'],
            moderator_id=row['moderator_id'],
            participants_id=row['known_participants_ids'],
            topic=row['topic'],
            link=row['link'],
            meeting_datetime=row['meeting_datetime'],
            created_at=row['created_at'],
            invitation_type=row['invitation_type'],
            remind_datetime=row['remind_datetime'],
            duration=row['duration'],
            author_id=row['author_id'],
            # unknown_participants_data=[json.loads(user) for user in row['unknown_participants_data']],
            # unknown_participants_data=row['unknown_participants_data'],
            status=row['status'],
        )
        local_tz = pytz.timezone('Europe/Moscow')
        meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        meeting.created_at = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)

        meeting.author_user = await self.users_repository.get_by_id(row['author_id'])
        meeting.moderator_user = await self.users_repository.get_by_id(row['moderator_id'])
        company_code = await self.companies_repository.get_company_code_by_company_id(row['company_id'])
        meeting.company_code = company_code[0]['company_code']

        known_participants_users = []
        for known_participant_id in row['known_participants_ids']:
            user = await self.users_repository.get_by_id(known_participant_id)
            known_participants_users.append(user)
        meeting.known_participants_users = known_participants_users
   
        try:
            unknown_participants = [json.loads(user) for user in row['unknown_participants_data']]
            unknown_participants_users = [UnknownUser(**unknown_participant) for unknown_participant in unknown_participants]
        except json.decoder.JSONDecodeError as e:
            unknown_participants = []
            unknown_participants_users = []
        meeting.unknown_participants_users = unknown_participants_users
        meeting.unknown_participants_data = unknown_participants

        return meeting
