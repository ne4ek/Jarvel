from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_menu_mailing_filling_keyboard(data_completely_filled=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    #go_to_menu_main_button = InlineKeyboardButton(text="В главное меню", callback_data="user_go_to mailing_menu_main")
    #if data_completely_filled:
    #    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Сохранить задачу", callback_data="task_save")])

    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="Изменить автора письма", callback_data="mailing_filling_change author")],
        [InlineKeyboardButton(text="Изменить шапку письма", callback_data="mailing_filling_change topic")],
        [InlineKeyboardButton(text="Изменить тело письма", callback_data="mailing_filling_change body")],
        [InlineKeyboardButton(text="Изменить получателей", callback_data="mailing_filling_change recipients")],
        [InlineKeyboardButton(text="Добавить вложенные файлы", callback_data="mailing_filling_change attachment")],
        [InlineKeyboardButton(text="Удалить", callback_data="mailing_filling_delete")],
        #добавить изменение способа связи
        #добавить изменения времени отправки
        #добавить изменения способа отправки
        #[go_to_menu_main_button]
    ])
    return keyboard

def get_save_mailing_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Cохранить письмо", callback_data="mailing_save")])
    return keyboard

def get_go_to_mailing_filling_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="mailing_filling back")])
    return keyboard
