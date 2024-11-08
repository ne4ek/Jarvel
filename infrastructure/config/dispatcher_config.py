from aiogram import Dispatcher
from infrastructure.config.group_chats import dispatcher_group_chats_config
from infrastructure.config.user_chats.dispatcher_user_chats_config import include_routers
from infrastructure.config import middlewares_config

dp = Dispatcher()


def config():
    dispatcher_group_chats_config.config(dp)
    
    include_routers(dp)
    middlewares_config.config(dp)
