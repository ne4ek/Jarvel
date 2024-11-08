CREATE TABLE users (
    user_id BIGINT,
    username TEXT,
    name TEXT,
    email TEXT,
    personal_link TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE messages (
    message_id SERIAL PRIMARY KEY,
    chat_message_id BIGINT,
    author_id BIGINT,
    company_code TEXT,
    text TEXT,
    date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    code TEXT,
    name TEXT,
    description TEXT,
    owner_id BIGINT,
    users_id BIGINT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE user_chats (
    chat_id BIGINT,
    role TEXT,
    company_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE group_chats (
    chat_id BIGINT,
    name TEXT,
    company_code TEXT,
    owner_id BIGINT,
    admins_id BIGINT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    author_id BIGINT,
    executor_id BIGINT,
    task TEXT,
    deadline TIMESTAMP WITH TIME ZONE,
    task_summary TEXT,
    status TEXT,
    tag TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE scheduler_jobs (
    job_id SERIAL PRIMARY KEY,
    type TEXT,
    trigger TEXT,
    run_date TIMESTAMP WITH TIME ZONE,
    sender_username TEXT,
    chat_id BIGINT,
    users_mentioned_usernames TEXT,
    reply_message_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE meetings (
    meeting_id SERIAL PRIMARY KEY,
    moderator_id BIGINT,
    participants_id BIGINT[],
    author_id BIGINT,
    topic TEXT,
    link TEXT,
    company_code TEXT,
    invitation_type TEXT,
    duration TEXT,
    meeting_time TIMESTAMP WITH TIME ZONE,
    remind_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE mailing (
    mailing_id SERIAL PRIMARY KEY,
    author_id BIGINT,
    recipient_ids BIGINT[],
    topic TEXT,
    body TEXT,
    contact_type TEXT,
    attachment TEXT[],
    send_delay TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);