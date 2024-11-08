from aiogram.utils.keyboard import CallbackData


class MenuMeetingsPaginator(CallbackData, prefix="menu_meetings"):
    company_code: str


class MeetingsListPaginator(CallbackData, prefix="list_of_meetings"):
    meeting_id: int
    company_code: str


class TaskListPaginator(CallbackData, prefix="list_of_meetings"):
    meeting_id: int
    company_code: str


class CompaniesPaginator(CallbackData, prefix="pag"):
    company_code: str
    tasks_type: str
    sort_type: str


class DeadlineTaskSortPaginator(CallbackData, prefix="deadline_sort_pag"):
    company_code: str
    deadline_type: str
    tasks_type: str


class DeadlineMeetingSortPaginator(CallbackData, prefix="deadline_sort_pag"):
    company_code: str
    deadline_type: str
    tasks_type: str

