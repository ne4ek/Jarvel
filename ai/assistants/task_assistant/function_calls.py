extract_task_data = [
    {
        "name": "extract_task_data",
        "description": "По запросу пользователя функция составляет задачу.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_author_name": {
                    "type": "string",
                    "description": "Имя заказчика, автор задачи.",
                },
                "executor_name": {
                    "type": "string",
                    "description": "Полное имя и фамилия (если указана) пользователя, назначенного исполнителем. '0', если не указан",
                },
                "deadline_date": {
                    "type": "string",
                    "description": "Дата дедлайна задачи ТОЛЬКО в формате dd.mm.yyyy. '0', если не указано",
                },
                "deadline_time": {
                    "type": "string",
                    "description": "Время дедлайна задачи ТОЛЬКО в формате HH:MM. '0', если не указано.",
                },
                "task": {
                    "type": "string",
                    "description": "Дословное описание задачи. '0', если не указано.",
                },
                "task_summary": {
                    "type": "string",
                    "description": "Краткое описание задачи в 3-4 словах. '0', если task не указано. Описание задачи без сокращений, если сокращать нечего."
                },
                "tag": {
                    "type": "string",
                    "description": "Тег задачи. Описание задачи, если оно состоит из одного слова",
                },
            },
            "required": [
                "task_author_name",
                "executor_name",
                "deadline_time",
                "deadline_date",
                "task",
                "task_summary",
                "tag"
            ],
        }
    }
]

change_task_author = [
    {
        "name": "change_task_author",
        "description": "Изменяет автора задачи по просьбе пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "task_author_name": {
                    "type": "string",
                    "description": "Новый автор задачи"
                }
            },
            "required": [
                "task_author_name"
            ]
        }
    }
]

change_task_executor = [
    {
        "name": "change_task_executor",
        "description": "Изменяет исполнителя задачи по просьбе пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "task_executor_name": {
                    "type": "string",
                    "description": "Новый исполнитель задачи"
                }
            },
            "required": [
                "task_executor_name"
            ]
        }
    }
]

change_task_deadline = [
    {
        "name": "change_task_deadline",
        "description": "Изменяет дедлайн задачи по просьбе пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "deadline_date": {
                    "type": "string",
                    "description": "Новая дата дедлайна задачи. Оставить без изменений, если дата не изменилась"
                },
                "deadline_time": {
                    "type": "string",
                    "description": "Новое время дедлайна задачи. Оставить без изменений, если дата не изменилась"
                }
            },
            "required": [
                "deadline_date",
                "deadline_time"
            ]
        }
    }
]


change_task_description = [
    {
        "name": "change_task_description",
        "description": "Редактирует или составляет описание задачи",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Развернутое описание задачи. '0', если не указано"
                },
                "task_summary": {
                    "type": "string",
                    "description": "Краткое описание задачи в 3-4 словах. '0', если task не указано"
                },
                "tag": {
                    "type": "string",
                    "description": "Тег задачи (одно слово).",
                }
            },
            "required": [
                "task",
                "task_summary",
                "tag"
            ]
        }
    }
]