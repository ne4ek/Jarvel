from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.meetings.services.user_chat_meeting_service import UserChatMeetingService

class MeetingNotificationsHandlers:
    def __init__(self, notification_meeting_service: UserChatMeetingService):
        self.notification_meeting_service = notification_meeting_service
    
    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_states(router)
        return router
    
    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.participant_accept_invitation_callback, F.data.startswith("meeting_participant confirm"))
        router.callback_query.register(self.participant_invitation_declined_callback, F.data.startswith("meeting_participant decline"))
        
    
    def __register_states(self, router: Router) -> None:
        pass
    
    
    async def participant_accept_invitation_callback(self, callback: types.CallbackQuery):
        response = self.notification_meeting_service.participant_meeting_accepted()
        text = response.get("text")
        keyboard = response.get("keyboard")
        
        await callback.message.edit_caption(caption=text, reply_markup=keyboard)
    
    async def participant_invitation_declined_callback(self, callback: types.CallbackQuery):
        meeting_id = int(callback.data.split("meeting_id:")[-1])
        response = await self.notification_meeting_service.participant_meeting_declined(meeting_id, callback.from_user.id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_caption(caption=text, reply_markup=keyboard)