from ai.assistants.mailing_assistant.function_tools import extract_mail_data, change_mail_author, change_mail_body, change_mail_recipients, change_mail_topic, change_mail_send_delay
from ai.assistants.mailing_assistant.mailing_assistant_prompts import mailing_assistant_compose, mailing_assistant_change_author, mailing_assistant_change_body, mailing_assistant_change_topic, mailing_assistant_change_recipients, mailing_assistant_change_send_delay
from ai.assistants.mailing_assistant.mailing_assistant import MailingAssistant
from infrastructure.providers_impl.function_calls_provider_impl import FunctionCallsProviderImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.prompts_provider_impl import PromptsProviderImpl
import os

mailing_assistant_function_call_provider = FunctionCallsProviderImpl()

prompts_provider = PromptsProviderImpl(change_mail_author=mailing_assistant_change_author,
                                       change_mail_body=mailing_assistant_change_body,
                                       change_mail_topic=mailing_assistant_change_topic,
                                       change_mail_recipients=mailing_assistant_change_recipients,
                                       change_mail_send_delay=mailing_assistant_change_send_delay
                                       )

mailing_assistant_function_call_provider.add_function_calls({"extract_mail_data": extract_mail_data,
                                                             "change_mail_author": change_mail_author,
                                                             "change_mail_body": change_mail_body,
                                                             "change_mail_topic": change_mail_topic,
                                                             "change_mail_recipients": change_mail_recipients,
                                                             "change_mail_send_delay": change_mail_send_delay
                                                             })

mailing_assistant = MailingAssistant(api_key=os.getenv("GPT_API_KEY"),
                                     model="gpt-4o-mini",
                                     temperature=0,
                                     initial_prompt=mailing_assistant_compose,
                                     functions_provider=mailing_assistant_function_call_provider,
                                     prompt_provider=prompts_provider,
                                     company_repository=repositroties_dependency_provider_async.get_companies_repository())