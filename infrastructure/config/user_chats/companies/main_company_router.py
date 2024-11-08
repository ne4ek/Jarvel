from aiogram import Router
from .company_registration_config import create_company_router
from .joining_company_config import join_company_router

main_company_router = Router()

main_company_router.include_routers(create_company_router,
                                    join_company_router)