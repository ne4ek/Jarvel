from aiogram import Dispatcher

from application.telegram.middlewares.check_user_registration import CheckRegistrationMiddleware
from application.telegram.middlewares.set_logs import SetLogMiddleware


def config(dp: Dispatcher):


    dp.message.middleware(CheckRegistrationMiddleware())
    dp.callback_query.middleware(CheckRegistrationMiddleware())
