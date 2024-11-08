from ai.assistants.talker.talker import Talker
from ai.assistants.talker.offline_talker import OfflineTalker
from ai.assistants.talker.online_talker import OnlineTalker
from ai.assistants.talker.talker_prompts import talker_prompt, get_talker_type_prompt
from ai.assistants.talker.function_calls import get_talker_type
from infrastructure.providers_impl.function_calls_provider_impl import FunctionCallsProviderImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from dotenv import load_dotenv
import os

load_dotenv()

offline_talker = OfflineTalker(api_key=os.getenv("GPT_API_KEY"),
                               model="gpt-4o-mini",
                               temperature=0.7,
                               prompt=talker_prompt)

online_talker = OnlineTalker(api_key=os.getenv("PPLX_API_KEY"),
                             model="llama-3-sonar-large-32k-online",
                             prompt=talker_prompt,
                             repositories_provider=repositroties_dependency_provider_async)

online_talker = offline_talker

function_provider = FunctionCallsProviderImpl()
function_provider.add_function_calls({"get_talker_type": get_talker_type})

talker = Talker(api_key=os.getenv("GPT_API_KEY"),
                model="gpt-4o-mini",
                temperature=0,
                get_talker_type_prompt=get_talker_type_prompt,
                talker_types={"offline": offline_talker,
                              "online": online_talker},
                functions_provider=function_provider)
