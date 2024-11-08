from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


go_to_group_menu_main = InlineKeyboardButton(text="🔙 В главное меню", callback_data="group_go_to main_menu")

def get_menu_mailing_filling_keyboard(data_completely_filled=False, go_to_main_menu=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    if data_completely_filled:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="📤 Отправить письмо", callback_data="mailing_filling_save")])

    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="👤 Изменить автора письма", callback_data="mailing_filling_change author")],
        [InlineKeyboardButton(text="✍️ Изменить тему письма", callback_data="mailing_filling_change topic")],
        [InlineKeyboardButton(text="📝 Изменить тело письма", callback_data="mailing_filling_change body")],
        [InlineKeyboardButton(text="👥 Изменить получателей", callback_data="mailing_filling_change recipients")],
        [InlineKeyboardButton(text="✔️ Изменить способ отправки", callback_data="mailing_filling_change contact_type")],
        [InlineKeyboardButton(text="⏳ Изменить задержку перед отправкой", callback_data="mailing_filling_change sending_delay")],
        [InlineKeyboardButton(text="📁 Добавить вложенные файлы", callback_data="mailing_filling_change attachment")]
    ])
    if go_to_main_menu:
        keyboard.inline_keyboard.append([go_to_group_menu_main])
    return keyboard

def get_go_to_mailing_filling_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="mailing_filling back")])
    return keyboard

def get_mailing_filling_contact_type_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="Телеграм", callback_data="mailing_filling contact_telegram")],
        [InlineKeyboardButton(text="📧 Почта", callback_data="mailing_filling contact_email")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="mailing_filling back")]
    ])
    return keyboard

def get_go_to_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[go_to_group_menu_main]])

def get_go_to_user_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])