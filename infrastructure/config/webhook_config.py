import ngrok
import os
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Dispatcher, Bot
from icecream import ic


load_dotenv()

async def config(dp: Dispatcher, bot: Bot):
    ic(os.getenv("NGROK_AUTH_TOKEN"))
    listener = await ngrok.forward(
    int(os.getenv("WEBAPP_PORT")), authtoken=os.getenv("NGROK_AUTH_TOKEN"), 
    )
    await bot.set_webhook(f"{listener.url()}/webhook", 
                          drop_pending_updates=True,)