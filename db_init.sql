CREATE TABLE IF NOT EXISTS public.company (
    company_id SERIAL PRIMARY KEY,
    name text NOT NULL,
    company_code text NOT NULL,
    description text,
    owner_id bigint
);


CREATE TABLE IF NOT EXISTS public.ctrls (
    chat_id bigint NOT NULL,
    run_date timestamp with time zone NOT NULL,
    ctrl_usernames text NOT NULL,
    reply_message_id bigint NOT NULL,
    fyi_usernames text NOT NULL
);


CREATE TABLE IF NOT EXISTS public.group_chat (
    group_chat_id bigint NOT NULL,
    name text NOT NULL,
    company_id smallint NOT NULL
);


CREATE TABLE IF NOT EXISTS public.mail (
    mail_id bigint NOT NULL,
    author_id bigint NOT NULL,
    known_recipients_ids bigint[] NOT NULL,
    unknown_recipients_data jsonb[],
    topic text NOT NULL,
    body text NOT NULL,
    contact_type text,
    send_delay smallint,
    send_at timestamp with time zone,
    attachment bytea[],
    company_id smallint NOT NULL
);


CREATE TABLE IF NOT EXISTS public.meeting (
    meeting_id bigint NOT NULL,
    author_id bigint NOT NULL,
    moderator_id bigint NOT NULL,
    topic text NOT NULL,
    link text NOT NULL,
    known_participants_ids bigint[],
    unknown_participants_data jsonb,
    meeting_datetime timestamp with time zone NOT NULL,
    remind_datetime timestamp with time zone NOT NULL,
    company_id smallint NOT NULL,
    duration smallint,
    invitation_type text NOT NULL,
    status text
);


CREATE TABLE IF NOT EXISTS public.message (
    message_id bigint NOT NULL,
    user_id bigint NOT NULL,
    text text NOT NULL,
    date timestamp with time zone NOT NULL,
    replied_message_id bigint,
    chat_id bigint
);



CREATE TABLE IF NOT EXISTS public.scheduler_jobs (
    job_id integer NOT NULL,
    type text,
    trigger text,
    run_date timestamp with time zone,
    sender_username text,
    chat_id bigint,
    users_mentioned_usernames text,
    reply_message_id bigint,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);




CREATE TABLE IF NOT EXISTS public.task (
    task_id bigint NOT NULL,
    author_id bigint NOT NULL,
    executor_id bigint NOT NULL,
    description text NOT NULL,
    task_summary text NOT NULL,
    tag text,
    deadline_datetime timestamp with time zone NOT NULL,
    status text NOT NULL,
    company_id smallint NOT NULL
);




CREATE TABLE IF NOT EXISTS public."user" (
    user_id bigint NOT NULL,
    username text NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL,
    arbitrary_data jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);



CREATE TABLE IF NOT EXISTS public.user_chat (
    user_chat_id bigint NOT NULL,
    company_id bigint,
    user_id bigint NOT NULL
);




CREATE TABLE IF NOT EXISTS public.user_company (
    user_id bigint,
    company_id smallint,
    role text,
    rights text
);


CREATE TABLE IF NOT EXISTS public.ups (
    up_id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    present_date TIMESTAMP WITH TIME ZONE NOT NULL,
    next_up_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    interval INTERVAL NOT NULL,
    starting_interval INTERVAL NOT NULL,
    up_username VARCHAR(255) NOT NULL,
    reply_message_id INT NOT NULL,
    bot_message_id INT DEFAULT NULL,
    fyi_username TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE IF NOT EXISTS public.transcribed_voice_message_text(
    transcribed_voice_message_text_id SERIAL PRIMARY KEY,
    text TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS public.tunneling(
    tunneling_id SERIAL PRIMARY KEY,
    specify_chat_pinned_message_id INT DEFAULT NULL,
    source_chat_pinned_message_id INT DEFAULT NUll,
    to_chat_id BIGINT NOT NULL,
    to_topic_id INT NOT NULL,
    from_chat_id BIGINT NOT NULL,
    from_topic_id INT NOT NULL
);


CREATE TABLE IF NOT EXISTS public.media_group(
    media_group_id BIGINT NOT NUll
);