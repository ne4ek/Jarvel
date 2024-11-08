--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Debian 16.4-1.pgdg120+1)
-- Dumped by pg_dump version 16.4 (Debian 16.4-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: jarvel_schema; Type: SCHEMA; Schema: -; Owner: jarvelpostgres
--

CREATE SCHEMA jarvel_schema;


ALTER SCHEMA jarvel_schema OWNER TO jarvelpostgres;

--
-- Name: company_id_seq; Type: SEQUENCE; Schema: public; Owner: jarvelpostgres
--

CREATE SEQUENCE public.company_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_id_seq OWNER TO jarvelpostgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: company; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.company (
    company_id smallint DEFAULT nextval('public.company_id_seq'::regclass) NOT NULL,
    name text NOT NULL,
    company_code text NOT NULL,
    description text,
    owner_id bigint
);


ALTER TABLE public.company OWNER TO jarvelpostgres;

--
-- Name: ctrls; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.ctrls (
    chat_id bigint NOT NULL,
    run_date timestamp with time zone NOT NULL,
    ctrl_usernames text NOT NULL,
    reply_message_id bigint NOT NULL,
    fyi_usernames text NOT NULL
);


ALTER TABLE public.ctrls OWNER TO jarvelpostgres;

--
-- Name: group_chat; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.group_chat (
    group_chat_id bigint NOT NULL,
    name text NOT NULL,
    company_id smallint NOT NULL
);


ALTER TABLE public.group_chat OWNER TO jarvelpostgres;

--
-- Name: mail; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.mail (
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


ALTER TABLE public.mail OWNER TO jarvelpostgres;

--
-- Name: meeting; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.meeting (
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


ALTER TABLE public.meeting OWNER TO jarvelpostgres;

--
-- Name: message; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.message (
    message_id bigint NOT NULL,
    user_id bigint NOT NULL,
    text text NOT NULL,
    date timestamp with time zone NOT NULL,
    replied_message_id bigint,
    chat_id bigint
);


ALTER TABLE public.message OWNER TO jarvelpostgres;

--
-- Name: scheduler_jobs; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.scheduler_jobs (
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


ALTER TABLE public.scheduler_jobs OWNER TO jarvelpostgres;

--
-- Name: scheduler_jobs_job_id_seq; Type: SEQUENCE; Schema: public; Owner: jarvelpostgres
--

CREATE SEQUENCE public.scheduler_jobs_job_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scheduler_jobs_job_id_seq OWNER TO jarvelpostgres;

--
-- Name: scheduler_jobs_job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jarvelpostgres
--

ALTER SEQUENCE public.scheduler_jobs_job_id_seq OWNED BY public.scheduler_jobs.job_id;


--
-- Name: task; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.task (
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


ALTER TABLE public.task OWNER TO jarvelpostgres;

--
-- Name: user; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public."user" (
    user_id bigint NOT NULL,
    username text NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    email text NOT NULL,
    arbitrary_data jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."user" OWNER TO jarvelpostgres;

--
-- Name: user_chat; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.user_chat (
    user_chat_id bigint NOT NULL,
    company_id bigint,
    user_id bigint NOT NULL
);


ALTER TABLE public.user_chat OWNER TO jarvelpostgres;

--
-- Name: user_company; Type: TABLE; Schema: public; Owner: jarvelpostgres
--

CREATE TABLE public.user_company (
    user_id bigint,
    company_id smallint,
    role text,
    rights text
);


ALTER TABLE public.user_company OWNER TO jarvelpostgres;

--
-- Name: scheduler_jobs job_id; Type: DEFAULT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.scheduler_jobs ALTER COLUMN job_id SET DEFAULT nextval('public.scheduler_jobs_job_id_seq'::regclass);


--
-- Name: company company_id; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.company
    ADD CONSTRAINT company_id PRIMARY KEY (company_id);


--
-- Name: group_chat group_chat_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.group_chat
    ADD CONSTRAINT group_chat_pkey PRIMARY KEY (group_chat_id);


--
-- Name: mail mail_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.mail
    ADD CONSTRAINT mail_pkey PRIMARY KEY (mail_id);


--
-- Name: meeting meeting_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.meeting
    ADD CONSTRAINT meeting_pkey PRIMARY KEY (meeting_id);


--
-- Name: message message_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_pkey PRIMARY KEY (message_id);


--
-- Name: scheduler_jobs scheduler_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.scheduler_jobs
    ADD CONSTRAINT scheduler_jobs_pkey PRIMARY KEY (job_id);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (task_id);


--
-- Name: user_chat user_chat_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public.user_chat
    ADD CONSTRAINT user_chat_pkey PRIMARY KEY (user_chat_id);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: jarvelpostgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- PostgreSQL database dump complete
--

