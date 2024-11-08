import logging
from aiogram import Bot
import os
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from infrastructure.logging.logs_setup import logs_settings
from infrastructure.config.bot_config import bot, get_bot_commands
from infrastructure.config import dispatcher_config
from infrastructure.repositories_impl.postgres.postgres_connection import close_all_connections
# from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import close_all_connections
from infrastructure.config.scheduler import config_scheduler
from infrastructure.config import webhook_config
from infrastructure.config.postgres_config_async import create_pool
from icecream import ic
import logging

logging.basicConfig(level=logging.INFO)

# последний коммит кокоса
async def on_startup(bot: Bot):
    await create_pool()
    await bot.set_my_commands(get_bot_commands())
    # Set routers and callbacks in
    dispatcher_config.config()
    await config_scheduler.config()
    await webhook_config.config(dp=dispatcher_config.dp, bot=bot)

def start_bot():
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dispatcher_config.dp,
        bot=bot,
        
    )
    webhook_requests_handler.register(app, path="/webhook")
    try:
        dispatcher_config.dp.startup.register(on_startup)
        setup_application(app, dispatcher_config.dp, bot=bot)
        web.run_app(
        app,
        host=os.getenv("WEBAPP_HOST"),
        port=int(os.getenv("WEBAPP_PORT"))
    )
    except Exception as e:
        logging.warning(e)
    finally:
        close_all_connections()

if __name__ == "__main__":
    logs_settings()
    start_bot()