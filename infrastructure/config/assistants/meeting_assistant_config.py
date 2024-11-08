from ai.assistants.meeting_assistant.meeting_assistant import MeetingAssistant
from ai.assistants.meeting_assistant.meeting_assistant_prompts import meeting_assistant_intro
from ai.assistants.meeting_assistant.function_calls import compose_all_meeting_dates, compose_all_meeting_extra_data, compose_all_meeting_participants
from ai.assistants.meeting_assistant.function_calls import change_meeting_duration, change_meeting_moderator, change_meeting_participants, change_meeting_remind_datetime, change_meeting_topic, change_meeting_datetime, change_meeting_link
from ai.assistants.meeting_assistant.meeting_assistant_prompts import change_meeting_topic_prompt, change_meeting_datetime_prompt, change_meeting_duration_prompt, change_meeting_moderator_prompt, change_meeting_participants_prompt, change_meeting_remind_datetime_prompt
from infrastructure.providers_impl.function_calls_provider_impl import FunctionCallsProviderImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.prompts_provider_impl import PromptsProviderImpl
import os
from dotenv import load_dotenv

load_dotenv()


function_calls_provider = FunctionCallsProviderImpl()

function_calls_provider.add_function_calls({"compose_all_meeting_dates": compose_all_meeting_dates,
                                           "compose_all_meeting_participants": compose_all_meeting_participants,
                                           "compose_all_meeting_extra_data": compose_all_meeting_extra_data,
                                           "change_meeting_topic": change_meeting_topic,
                                           "change_meeting_datetime": change_meeting_datetime,
                                           "change_meeting_duration": change_meeting_duration,
                                           "change_meeting_moderator": change_meeting_moderator,
                                           "change_meeting_participants": change_meeting_participants,
                                           "change_meeting_remind_datetime": change_meeting_remind_datetime})

prompt_provider = PromptsProviderImpl(change_meeting_topic=change_meeting_topic_prompt,
                                      change_meeting_datetime=change_meeting_datetime_prompt,
                                      change_meeting_duration=change_meeting_duration_prompt,
                                      change_meeting_moderator=change_meeting_moderator_prompt,
                                      change_meeting_participants=change_meeting_participants_prompt,
                                      change_meeting_remind_datetime=change_meeting_remind_datetime_prompt)

meeting_assistant = MeetingAssistant(api_key=os.getenv("GPT_API_KEY"),
                                     model="gpt-4o-mini",
                                     temperature=0,
                                     prompt=meeting_assistant_intro,
                                     functions_provider=function_calls_provider,
                                     company_repository=repositroties_dependency_provider_async.get_companies_repository(),
                                     change_data_prompts=prompt_provider)