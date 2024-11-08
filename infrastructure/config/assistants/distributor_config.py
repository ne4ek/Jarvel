from ai.assistants.distributor.distributor import Distributor
from ai.assistants.distributor.distributor_prompts import distributor_intro
from ai.assistants.distributor.function_calls import distibutor_func
from .task_assistant_config import task_assistant
from .mailing_assistant_config import mailing_assistant
from .meeting_assistant_config import meeting_assistant
from .talker_config import talker
from .arbitrary_data_manager_config import arbitrary_data_manager
import os
from dotenv import load_dotenv

load_dotenv()


distributor = Distributor(api_key=os.getenv("GPT_API_KEY"),
                          model="gpt-4o-mini",
                          temperature=0,
                          prompt=distributor_intro,
                          function=distibutor_func)

distributor.add_assistant({"task_assistant": task_assistant,
                           "mailing_assistant": mailing_assistant,
                           "meeting_assistant": meeting_assistant,
                           "talker": talker,
                           "arbitrary_data_manager": arbitrary_data_manager,
                           "no_assistant": None})