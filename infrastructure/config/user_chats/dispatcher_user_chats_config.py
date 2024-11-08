def include_routers(dp):
    from application.telegram.handlers.user_chats.initialization import user_chats_router

    dp.include_router(user_chats_router)