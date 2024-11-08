from ai.assistants.task_assistant.task_assistant import TaskAssistant
from ai.assistants.task_assistant.task_assistant_prompts import task_assistant_compose,\
                                                                task_assistant_change_author,\
                                                                task_assistant_change_executor,\
                                                                task_assistant_change_deadline, \
                                                                task_assistant_change_description
from ai.assistants.task_assistant.function_calls import extract_task_data, change_task_author,\
                                                        change_task_executor, change_task_deadline,\
                                                        change_task_description
from infrastructure.providers_impl.function_calls_provider_impl import FunctionCallsProviderImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.prompts_provider_impl import PromptsProviderImpl
import os


task_assistant_function_call_provider = FunctionCallsProviderImpl()

prompts_provider = PromptsProviderImpl(change_task_author=task_assistant_change_author,
                                       change_task_executor=task_assistant_change_executor,
                                       change_task_deadline=task_assistant_change_deadline,
                                       change_task_description=task_assistant_change_description)

task_assistant_function_call_provider.add_function_calls({"extract_task_data": extract_task_data,
                                                          "change_task_author": change_task_author,
                                                          "change_task_executor": change_task_executor,
                                                          "change_task_deadline": change_task_deadline,
                                                          "change_task_description": change_task_description})

task_assistant = TaskAssistant(api_key=os.getenv("GPT_API_KEY"),
                               model="gpt-4o-mini",
                               temperature=0,
                               initial_prompt=task_assistant_compose,
                               change_data_prompts=prompts_provider,
                               functions_provider=task_assistant_function_call_provider,
                               company_repository=repositroties_dependency_provider_async.get_companies_repository())
