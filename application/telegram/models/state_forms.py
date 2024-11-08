from aiogram.fsm.state import State, StatesGroup


class CompanyCreation(StatesGroup):
    choosing_company_name = State()
    choosing_company_description = State()


class Registration(StatesGroup):
    choosing_firstname = State()
    choosing_lastname = State()
    choosing_email = State()
    registered = State()
    choosing_role = State()


class MeetingArgs(StatesGroup):
    topic = State()
    meeting_time = State()
    remind_time = State()

    moderator_id = State()
    participants_id = State()

    invitation_type = State()
    link = State()
    duration = State()
    empty = State()


class JoinCompany(StatesGroup):
    company_code = State()
    choosing_role = State()


class PersonalLinkChange(StatesGroup):
    personal_link = State()


class PersonalInfoChange(StatesGroup):
    choosing_firstname = State()
    choosing_lastname = State()
    choosing_email = State()
    empty = State()


class TaskState(StatesGroup):
    change_author = State()
    change_executor = State()
    change_deadline = State()
    change_decription = State()
    change_tag = State()
    empty = State()

class MailingState(StatesGroup):
    empty = State()
    change_author = State()
    change_topic = State()
    change_body = State()
    change_attachment = State()
    change_recipients = State()
    change_contact_type = State()
    change_send_delay = State()

class UserMailingState(MailingState):
    pass

class MeetingState(StatesGroup):
    change_topic = State()
    change_meeting_time = State()
    change_remind_time = State()

    change_moderator = State()
    change_participants = State()

    change_invitation_type = State()
    change_link = State()
    change_duration = State()
    empty = State()

class MeetingUserChatState(StatesGroup):
    moderator_change_link = State()
    
class MeetingMenuState(StatesGroup):
    moderator_change_link = State()
    moderator_change_datetime = State()

class PersonalTaskChange(StatesGroup):
    user_changing_data = State()
    change_description = State()
    change_tag = State()
    change_deadline = State()

class AuthorTaskChange(StatesGroup):
    author_changing_data = State()
    change_description = State()
    change_tag = State()
    change_deadline = State()