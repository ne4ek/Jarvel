from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

go_to_group_menu_main = InlineKeyboardButton(text="В главное меню", callback_data="group_go_to main_menu")

def get_menu_meeting_filling_keyboard(data_completely_filled=False, go_to_main_menu=False):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    if data_completely_filled:
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Сохранить встречу", callback_data="meeting_save")])

    keyboard.inline_keyboard.extend([
            [InlineKeyboardButton(text="📌 Изменить тему встречи", callback_data="meeting_filling_change topic")],
            [InlineKeyboardButton(text="⏰ Изменить время встречи", callback_data="meeting_filling_change meeting_time")],
            [InlineKeyboardButton(text="⏳ Изменить время напоминания до встречи", callback_data="meeting_filling_change remind_time")],
            [InlineKeyboardButton(text="👤 Изменить модератора встречи", callback_data="meeting_filling_change moderator")],
            [InlineKeyboardButton(text="👥 Изменить участников", callback_data="meeting_filling_change participants")],
            [InlineKeyboardButton(text="🔗 Изменить ссылку", callback_data="meeting_filling_change link")],
            [InlineKeyboardButton(text="📍 Изменить тип напоминания", callback_data="meeting_filling_change invitation_type")],
            [InlineKeyboardButton(text="🕒 Изменить продолжительность встречи", callback_data="meeting_filling_change duration")],
        ])
    if go_to_main_menu:
        keyboard.inline_keyboard.append([go_to_group_menu_main])
    return keyboard

def get_main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    

def get_go_to_menu_meetings_filling():
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="meeting_filling back")],
        ]
    )
    return button


def get_go_to_main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[[go_to_group_menu_main]])

def get_change_invitation_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Телеграм", callback_data="meeting_filling_change invitation_type:telegram")],
        [InlineKeyboardButton(text="Почта", callback_data="meeting_filling_change invitation_type:email")],
        [go_to_group_menu_main]
    ])