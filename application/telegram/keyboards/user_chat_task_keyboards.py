from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from icecream import ic
from application.telegram.keyboards.keybords_paginators import CompaniesPaginator, DeadlineTaskSortPaginator, TaskListPaginator


go_to_menu_main_button = InlineKeyboardButton(text="Вернуться в главное меню", callback_data="user_go_to menu_main")


def get_go_to_menu_main():
    """Функция возвращает кнопку для возврата в главное меню из любой точки кода"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [go_to_menu_main_button],
        ]
    )
    return keyboard


def menu_tasks_and_orders(company_code: str):
    """Фукнция возвращает клавиатуру меню задач и заказов с сохраниеим company_code"""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Полученные", callback_data=f"user_go_to menu_tasks company_code:{company_code}")],
            [InlineKeyboardButton(text="Поставленные", callback_data=f"user_go_to menu_orders company_code:{company_code}")],
            [InlineKeyboardButton(text="Архив", callback_data=f"user_go_to menu_archive company_code:{company_code}")],
            [InlineKeyboardButton(text="К выбору компании", callback_data="user_go_to choose_company_tasks")],
            [go_to_menu_main_button],
        ]
    )
    return keyboard


def menu_tasks(company_code):
    """Функция возвращает клавиатуру меню задач"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="По тегу", callback_data=CompaniesPaginator(
                company_code=company_code,
                tasks_type="tasks",
                sort_type="tag").pack()),
             InlineKeyboardButton(text="По дедлайну", callback_data=CompaniesPaginator(
                company_code=company_code,
                tasks_type="tasks",
                sort_type="deadline").pack())],
            [InlineKeyboardButton(text="Назад",
                                  callback_data=f"user_go_to menu_tasks_and_orders company_code:{company_code}"),
             go_to_menu_main_button],
        ]
    )
    return keyboard


def menu_orders(company_code):
    """Функция возвращает клавиатуру меню заказов"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="По тегу", callback_data=CompaniesPaginator(
                company_code=company_code,
                tasks_type="orders",
                sort_type="tag").pack()),
             InlineKeyboardButton(text="По дедлайну", callback_data=CompaniesPaginator(
                company_code=company_code,
                tasks_type="orders",
                sort_type="deadline").pack())],
            [InlineKeyboardButton(text="Назад",
                                  callback_data=f"user_go_to menu_tasks_and_orders company_code:{company_code}"),
             go_to_menu_main_button],
        ]
    )
    return keyboard


def menu_archive(company_code):
    """Функция возвращает клавиатуру меню архива"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад",
                                  callback_data=f"user_go_to menu_tasks_and_orders company_code:{company_code}"),
             go_to_menu_main_button],
        ]
    )
    return keyboard


def task_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Мои задачи", callback_data="my_tasks"),
                InlineKeyboardButton(text="Мои заказы", callback_data="my_orders"),
            ],
            [InlineKeyboardButton(text="<<", callback_data="main_menu")],
        ]
    )

    return buttons


def my_orders_keyboard() -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Активные", callback_data="active_orders"),
                InlineKeyboardButton(
                    text="Завершенные", callback_data="completed_orders"
                ),
            ],
            [InlineKeyboardButton(text="<<", callback_data="task_menu")],
        ]
    )

    return buttons


def my_tasks_keyboard() -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Активные", callback_data="active_tasks"),
                InlineKeyboardButton(
                    text="Завершенные", callback_data="completed_tasks"
                ),
            ],
            [InlineKeyboardButton(text="<<", callback_data="task_menu")],
        ]
    )

    return buttons


def tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for n, task in enumerate(tasks):
        builder.button(text=f"{n + 1}", callback_data=task)

    builder.row(InlineKeyboardButton(text="<<", callback_data="task_menu"))

    return builder.as_markup()


def task_management_keyboard(task_id: str) -> InlineKeyboardMarkup:
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅", callback_data=f"mark_task_complete_{task_id}"
                )
            ],
            [InlineKeyboardButton(text="<<", callback_data="task_menu")],
        ]
    )

    return buttons


def confirm_task_keyboard() -> InlineKeyboardMarkup:
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                # TODO здесь в callback_data нужно передавать класс данных
                # Ниже прикреплена ссылка на плейлист, в одном из видео которого рассказывается как это сделать
                # https://www.youtube.com/watch?v=jORoDnYZhmc&list=PLEYdORdflM3lkbY2N9mH8pfH_-wPR9q9R

                text='Сохранить', callback_data=""
            )]
        ]
    )
    return button


def menu_tags_sort_types(company_code, tasks_type):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"user_go_to menu_{tasks_type} company_code:{company_code}"),
             go_to_menu_main_button],
        ]
    )
    return keyboard


def menu_tasks_deadline_sort_types(company_code, tasks_type):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сегодня", callback_data=DeadlineTaskSortPaginator(
                company_code=company_code,
                deadline_type="today",
                tasks_type=tasks_type).pack())],

            [InlineKeyboardButton(text="Неделя", callback_data=DeadlineTaskSortPaginator(
                company_code=company_code,
                deadline_type="week",
                tasks_type=tasks_type).pack())],

            [InlineKeyboardButton(text="2 Недели", callback_data=DeadlineTaskSortPaginator(
                company_code=company_code,
                deadline_type="2week",
                tasks_type=tasks_type).pack())],

            [InlineKeyboardButton(text="Месяц", callback_data=DeadlineTaskSortPaginator(
                company_code=company_code,
                deadline_type="month",
                tasks_type=tasks_type).pack())],

            [InlineKeyboardButton(text="Назад", callback_data=f"user_go_to menu_{tasks_type} company_code:{company_code}"),
             go_to_menu_main_button],
        ]
    )
    
    return keyboard


def menu_task_deadline_sort(company_code: str, tasks_type: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=CompaniesPaginator(
                company_code=company_code,
                tasks_type=tasks_type,
                sort_type="deadline").pack()),
             go_to_menu_main_button]
        ]
    )
    return keyboard


# TODO передать, чтобы можно было передавать сущность Task а не словарь
def get_builder_tasks_list(tasks_list, company_code: str):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for i, task in enumerate(tasks_list):
        # ic(i, task)
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=f"{i + 1}. {task.get('topic')}",
                                  callback_data=TaskListPaginator(
                                      meeting_id=task.get('meeting_id'),
                                      company_code=company_code).pack())
             ]
        )
    # ic(keyboard)
    keyboard.inline_keyboard.extend([
        [InlineKeyboardButton(text="По времени встречи", callback_data=CompaniesPaginator(
            company_code=company_code,
            tasks_type="meetings",
            sort_type="deadline").pack())],
        [InlineKeyboardButton(text="К выбору компании", callback_data="user_go_to choose_company_meetings")],
        [go_to_menu_main_button]
    ])
    # keyboard.inline_keyboard.append(
    #     [InlineKeyboardButton(text="По времени встречи", callback_data=CompaniesPaginator(
    #         company_code=company_code,
    #         tasks_type="meetings",
    #         sort_type="deadline").pack())])
    #
    # keyboard.inline_keyboard.append(
    #     [InlineKeyboardButton(text="К выбору компании", callback_data="user_go_to choose_company_meetings")])
    # keyboard.inline_keyboard.append([go_to_menu_main_button])
    return keyboard