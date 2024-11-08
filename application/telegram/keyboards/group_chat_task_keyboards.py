from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from application.telegram.keyboards.group_chat_keyboards import go_to_group_menu_main


def get_menu_task_filling_keyboard(data_completely_filled=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    if data_completely_filled:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Сохранить задачу", callback_data="task_save")])

    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="Изменить автора задачи", callback_data="task_filling_change author")],
        [InlineKeyboardButton(text="Изменить исполнителя", callback_data="task_filling_change executor")],
        [InlineKeyboardButton(text="Изменить дедлайн", callback_data="task_filling_change deadline")],
        [InlineKeyboardButton(text="Изменить содержание задачи", callback_data="task_filling_change task")],
        [InlineKeyboardButton(text="Изменить тег", callback_data="task_filling_change tag")],
        [InlineKeyboardButton(text="Удалить", callback_data="meeting_filling_delete")],
        [go_to_group_menu_main]
    ])
    return keyboard


def get_save_task_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Cохранить задачу", callback_data="task_save")])
    return keyboard

def get_go_to_filling_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="task_filling back")])
    return keyboard