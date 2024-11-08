from ai.arbitrary_data_manager.function_calls import arbitrary_data_action, get_action_functions, update_action_function
from ai.arbitrary_data_manager.arbitrary_data_manager import ArbitraryDataManager
from ai.arbitrary_data_manager.extractor_prompts import arbitrary_data_action_prompt, get_name_arbitary_data_prompt,\
                                                        get_user_arbitrary_data_prompt, update_arbitrary_data_prompt
from infrastructure.providers_impl.function_calls_provider_impl import FunctionCallsProviderImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from dotenv import load_dotenv
import os

load_dotenv()

functions_provider = FunctionCallsProviderImpl()
functions_provider.add_function_calls({"arbitrary_data_action": arbitrary_data_action,
                                       "get_action_functions": get_action_functions,
                                       "update_action_function": update_action_function})

arbitrary_data_manager = ArbitraryDataManager(api_key=os.getenv("GPT_API_KEY"),
                                              model="gpt-4o-mini",
                                              temperature=0,
                                              get_action_prompt=arbitrary_data_action_prompt,
                                              get_name_prompt=get_name_arbitary_data_prompt,
                                              get_user_data_prompt=get_user_arbitrary_data_prompt,
                                              update_user_data_prompt=update_arbitrary_data_prompt,
                                              functions_provider=functions_provider,
                                              repositories_proivider=repositroties_dependency_provider_async)