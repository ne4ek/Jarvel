from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from application.users.user_registration.services.registration_service import RegistrationService
from application.telegram.models.state_forms import Registration
from application.telegram.keyboards.start_keyboards import get_start_keyboard
from application.telegram.keyboards.user_chat_keyboards import go_to_menu_main_button
from application.companies.services.join_company_service import JoinCompanyService

jarvel_start_text = \
'''
Привет! 
Я — Jarvel, твой виртуальный ассистент.

Я создан, чтобы упростить твою рабочую коммуникацию и взять на себя рутинные задачи, чтобы ты мог сосредоточиться на главном.

Познакомься со мной поближе — вот <a href='https://docs.google.com/presentation/d/1-o2wYOnsg3iicf5A7MUzGCNOO1bB7SIm-fqw9pxX-Ic/edit?usp=sharing'>презентация</a> с моими основными функциями.

Чтобы узнать больше о том, как я работаю, посмотри <a href='https://docs.google.com/document/d/1T8O0AjFGCoHoHlVJ-M8ZnssSAjaZyvNXESRoEYvMpX8/edit?usp=sharing'>руководство пользователя</a>.

Если у тебя есть предложения или замечания, не стесняйся делиться ими через эту <a href='https://forms.gle/i6oo7GrTMDAdaSjK8'>форму обратной связи</a>.
'''


class UserRegistrationHandlers:
    def __init__(self, registration_service: RegistrationService, companies_service: JoinCompanyService):
        self.registration_service = registration_service
        self.companies_service = companies_service

    def get_router(self):
        router = Router()
        self.register_all_handlers(router)
        self.register_all_callbacks(router)
        return router

    def register_all_handlers(self, router: Router):
        router.message(Registration.choosing_firstname, F.chat.type == "private")(self.process_first_name)
        router.message(Registration.choosing_lastname, F.chat.type == "private")(self.process_lastname)
        router.message(Registration.choosing_email, F.chat.type == "private")(self.process_email)
        router.message(Command("start"), F.chat.type == "private")(self.start_command_handler)
        router.message(Command("registration"), F.chat.type == "private")(self.registration_command_handler)

    def register_all_callbacks(self, router: Router):
        router.callback_query.register(self.start_registration_callback, F.data == "start_user_registration")

    async def start_command_handler(self, message: types.Message, state: FSMContext):
        await state.clear()
        is_user_registered = await self.registration_service.is_user_registered(message.from_user.id)
        if is_user_registered:
            text = jarvel_start_text + "\n\nТы уже зарегистрирован"
            await message.answer(text=text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[go_to_menu_main_button]]), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        else:
            await message.answer(text=jarvel_start_text, reply_markup=get_start_keyboard(), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    
    
    async def start_registration_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.answer()
        if callback.from_user.username is None:
            await callback.message.answer("Для корректной работы необходимо, чтобы у вас был установлен юзернейм")
            return
        is_user_registered = await self.registration_service.is_user_registered(callback.from_user.id)
        if is_user_registered:
            await callback.message.answer("Вы уже зарегистрированы!")
            return
        await callback.message.answer("Для начала укажи своё имя (без фамилии)")
        await state.set_state(Registration.choosing_firstname)
        await state.update_data(user_id=callback.from_user.id)
        await state.update_data(username=callback.from_user.username)
    
    async def registration_command_handler(self, message: types.Message, state: FSMContext):
        if message.from_user.username is None:
            await message.answer("Для корректной работы необходимо, чтобы у вас был установлен юзернейм")
            return
        is_user_registered = await self.registration_service.is_user_registered(message.from_user.id)
        if is_user_registered:
            await message.answer("Вы уже зарегистрированы!")
            return
        await message.answer("Для начала укажи своё имя (без фамилии)")
        await state.set_state(Registration.choosing_firstname)
        await state.update_data(user_id=message.from_user.id)
        await state.update_data(username=message.from_user.username)
    
    async def process_first_name(self, message: types.Message, state:FSMContext):
        firstname = message.text
        await state.update_data(firstname=firstname)
        await state.set_state(Registration.choosing_lastname)
        await message.answer("Теперь укажи свою фамилию")
    
    async def process_lastname(self, message: types.Message, state:FSMContext):
        lastname = message.text
        await state.update_data(lastname=lastname)
        await state.set_state(Registration.choosing_email)
        await message.answer("И наконец свою почту!")
    
    async def process_email(self, message: types.Message, state:FSMContext):
        email = message.text
        
        if not self.registration_service.is_email_valid(email):
            await message.answer("Некорректные формат почты! Проверьте корректность введеной почты и повторите попытку")
            return
        await state.update_data(email=email)
        
        user_data = await state.get_data()
        await self.registration_service.save_user(user_data)
        
        await state.clear()
    
        await message.answer("Спасибо за регистрацию! Вы автоматически были добавлены к компании Belomorie.")
        user_chat = self.companies_service.create_user_chat(message.from_user.id)
        await self.companies_service.set_company_code("Belomorie", user_chat)
        self.companies_service.set_role("cool_person", user_chat)
        await self.companies_service.save_user(user_chat)