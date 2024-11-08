from datetime import datetime
from typing import List

from domain.entities.meeting import Meeting
from domain.entities.unknown_user import UnknownUser
from application.repositories.meetings_repository import MeetingsRepository
from application.repositories.users_repository import UsersRepository
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection, \
    reform_ro_dictionary
from psycopg2.pool import ThreadedConnectionPool
import json
import pytz
from icecream import ic



class PostgresMeetingsRepository(MeetingsRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool, users_repository: UsersRepository):
        self.db_connection_pool = db_connection_pool
        self.users_repository = users_repository

    @open_and_close_connection
    def save(self, meeting: Meeting, conn=None, cursor=None) -> int:
        ic(json.dumps(meeting.unknown_participants_data))
        sql_query = (
            "INSERT INTO meetings (author_id, moderator_id, participants_id, topic, link, meeting_time, invitation_type,"
            "remind_time, duration, company_code, unknown_participants_data, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING meeting_id;"
        )
        sql_values = (
            meeting.author_id,
            meeting.moderator_id,
            meeting.participants_id,
            meeting.topic,
            meeting.link,
            meeting.meeting_datetime,
            meeting.invitation_type,
            meeting.remind_datetime,
            meeting.duration,
            meeting.company_code,
            json.dumps(meeting.unknown_participants_data),
            "pending"
        )
        cursor.execute(sql_query, sql_values)
        meeting_id = cursor.fetchone()[0]
        conn.commit()
        return meeting_id

    @open_and_close_connection
    def get_all(self, conn=None, cursor=None) -> list[Meeting]:
        cursor.execute("SELECT * FROM meetings")
        rows = cursor.fetchall()
        list_of_meetings = []
        moderator_ids = {}
        author_ids = {}
        known_participants_ids = {}

        for row in rows:
            # Assuming the row order matches the Meeting class fields
            meeting = Meeting(
                meeting_id=row[0],
                moderator_id=row[1],
                participants_id=row[2],
                topic=row[3],
                link=row[4] if row[4] else None,
                meeting_datetime=row[5],
                created_at=row[6],
                invitation_type=row[7],
                remind_datetime=row[8],
                duration=row[9],
                author_id=row[10],
                company_code=row[11],
                unknown_participants_data=[json.loads(user) for user in row[12]],
                status=row[13]
            )
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            # Fetch author user
            if row[10] not in author_ids:
                author_ids[row[10]] = self.users_repository.get_by_id(row[10])
            meeting.author_user = author_ids[row[10]]

            # Fetch moderator user
            if row[1] not in moderator_ids:
                moderator_ids[row[1]] = self.users_repository.get_by_id(row[1])
            meeting.moderator_user = moderator_ids[row[1]]

            # Fetch known participants users
            known_participants_users = []
            for known_participant_id in row[2]:
                if known_participant_id not in known_participants_ids:
                    known_participants_ids[known_participant_id] = self.users_repository.get_by_id(known_participant_id)
                known_participants_users.append(known_participants_ids[known_participant_id])
            meeting.known_participants_users = known_participants_users

            # Deserialize and assign unknown participants users
            unknown_participants = [json.loads(user) for user in row[12]]
            unknown_participants_users = [UnknownUser(**unknown_participant) for unknown_participant in unknown_participants]
            meeting.unknown_participants_users = unknown_participants_users

            list_of_meetings.append(meeting)

        return list_of_meetings

    @open_and_close_connection
    def get_all_meeting_ids(self, conn=None, cursor=None) -> List[int]:
        cursor.execute("SELECT meeting_id FROM meetings")
        return [row[0] for row in cursor.fetchall()]

    @open_and_close_connection
    def get_by_user_id(self, user_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT * FROM meetings WHERE moderator_id = '{user_id}' OR {user_id} = ANY(participants_id)")
        lst = []
        for item in cursor.fetchall():
            meeting = Meeting(**item)
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            lst.append(meeting)
        return lst

    @open_and_close_connection
    def get_last_n_by_user_id(self, user_id: int, n: int, conn=None, cursor=None):
        cursor.execute(f"SELECT * FROM meetings "
                       f"WHERE moderator_id = '{user_id}' OR {user_id} = ANY(participants_id) "
                       f"ORDER BY meeting_time ASC LIMIT {n} ")
        lst = []
        for item in cursor.fetchall():
            meeting = Meeting(**item)
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            lst.append(meeting)
        return lst

    @open_and_close_connection
    def get_by_user_id_filter_deadline(self, user_id: int, deadline: datetime, conn=None, cursor=None):
        sql_request = f"SELECT * FROM meetings WHERE (moderator_id = {user_id} OR {user_id} = ANY(participants_id)) "

        datetime_sql_part = ("AND meeting_time AT TIME ZONE 'Europe/Moscow' <= "
                             "DATE_TRUNC('day', NOW()) + "
                             "INTERVAL '{} days' + INTERVAL '{} hour' + INTERVAL '{} minutes' ").format(
            deadline,
            deadline.hour,
            deadline.minute
        )
        sql_request += datetime_sql_part
        sql_request += "ORDER BY meeting_time ASC"
        cursor.execute(sql_request)
        return reform_ro_dictionary(cursor)

    @open_and_close_connection
    def get_by_meeting_id(self, meeting_id: int, conn=None, cursor=None):
        query = f"SELECT * FROM meetings WHERE meeting_id = %s"
        cursor.execute(query, (meeting_id,))
        row = cursor.fetchone()
        meeting = Meeting(
                meeting_id=row[0],
                moderator_id=row[1],
                participants_id=row[2],
                topic=row[3],
                link=row[4] if row[4] else None,
                meeting_datetime=row[5],
                created_at=row[6],
                invitation_type=row[7],
                remind_datetime=row[8],
                duration=row[9],
                author_id=row[10],
                company_code=row[11],
                status=row[13]
            )
        unknown_participants_data=[json.loads(user) for user in row[12]]
        known_participants_users = []
        local_tz = pytz.timezone('Europe/Moscow')
        meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        for known_participant_id in row[2]:
                known_participants_users.append(self.users_repository.get_by_id(known_participant_id))
        meeting.known_participants_users = known_participants_users
        meeting.unknown_participants_data = unknown_participants_data
        meeting.participants_users = {"known_participants": known_participants_users, "unknown_participants": [UnknownUser(**unknown_participant) for unknown_participant in unknown_participants_data]}
        meeting.moderator_user = self.users_repository.get_by_id(meeting.moderator_id)
        return meeting

    @open_and_close_connection
    def get_by_user_id_and_company_code(self, user_id: int, company_code: str, conn=None, cursor=None):
        query = f"SELECT * FROM meetings WHERE (moderator_id = %s OR %s = ANY(participants_id)) AND company_code = %s"
        cursor.execute(query, (user_id, user_id, company_code))
        lst = []
        for item in cursor.fetchall():
            meeting = Meeting(*item)
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            lst.append(meeting)
        return lst
    
    @open_and_close_connection
    def get_by_moderator_id_and_company_code(self, moderator_id: int, company_code: str, status: str = None, conn=None, cursor=None):
        if status:
            cursor.execute(f"SELECT * FROM meetings WHERE moderator_id = {moderator_id} AND company_code = '{company_code}' AND status = '{status}'")
        else:
            cursor.execute(f"SELECT * FROM meetings WHERE moderator_id = {moderator_id} AND company_code = '{company_code}'")
        lst = []
        for item in cursor.fetchall():
            meeting = Meeting(*item)
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            lst.append(meeting)
        return lst
    
    @open_and_close_connection
    def get_by_participant_id_and_company_code(self, participant_id: int, company_code: str, status: str = None, conn=None, cursor=None):
        if not status:
            cursor.execute(f"SELECT * FROM meetings WHERE {participant_id} = ANY(participants_id) AND company_code = '{company_code}'")
        else:
            cursor.execute(f"SELECT * FROM meetings WHERE {participant_id} = ANY(participants_id) AND company_code = '{company_code}' AND status = '{status}'")
        lst = []
        for item in cursor.fetchall():
            meeting = Meeting(*item)
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            lst.append(meeting)
        return lst
    
    @open_and_close_connection
    def set_link(self, meeting_id: int, link: str, conn=None, cursor=None):
        cursor.execute(f"UPDATE meetings SET link = '{link}' WHERE meeting_id = {meeting_id}")
        conn.commit()
    
    @open_and_close_connection
    def set_status(self, meeting_id: int, status: str, conn=None, cursor=None):
        cursor.execute(f"UPDATE meetings SET status = '{status}' WHERE meeting_id = {meeting_id}")
        conn.commit()
    
    @open_and_close_connection
    def set_participants(self, participants_ids: list[int], meeting_id: int, conn=None, cursor=None):
        sql_query = f"UPDATE meetings SET participants_id = %s WHERE meeting_id = %s"
        sql_values = (participants_ids, meeting_id)
        cursor.execute(sql_query, sql_values)
        conn.commit()
    
    @open_and_close_connection
    def set_meeting_datetime(self, meeting: Meeting, conn=None, cursor=None):
        sql_query = f"UPDATE meetings SET meeting_time = %s, remind_time = %s WHERE meeting_id = %s"
        sql_values = (meeting.meeting_datetime, meeting.remind_datetime, meeting.meeting_id)
        cursor.execute(sql_query, sql_values)
        conn.commit()
        
    @open_and_close_connection
    def get_by_status_and_company_code_and_user_id(self, status: str, user_id: int, company_code: str, conn=None, cursor=None):
        query = "SELECT * FROM meetings WHERE (%s = ANY(participants_id) OR %s = moderator_id) AND company_code = %s AND status = %s"
        values = (user_id, user_id, company_code, status)
        cursor.execute(query, values)
        lst = []
        for item in cursor.fetchall():
            meeting = Meeting(*item)
            local_tz = pytz.timezone('Europe/Moscow')
            meeting.meeting_datetime = meeting.meeting_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            meeting.remind_datetime = meeting.remind_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            lst.append(meeting)
        return lst