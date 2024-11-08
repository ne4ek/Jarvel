arbitrary_data_action = [
    {
        "name": "arbitrary_data_action",
        "description": "Возращает действие, которое нужно произвести над произвольными данными пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Действие над произвольными данными. GET - получить данные, UPDATE - обновить данные"
                }
            },
            "required": [
                "action"
            ]
        }
    }
]

get_action_functions = [
    {
        "name": "get_name",
        "description": "Возращает имя пользователя, данные которого нужно вывести",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Имя пользователя, данные которого необходимо предоставить."
                }
            },
            "required": [
                "name"
            ]
        }
    },
    {
        "name": "get_user_arbitrary_data",
        "description": "Возращает запрашиваемые данные пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Список из пар ключ:значение - запрашиваемые данные пользователя. Ключ - название искомого значения, значение - данные о пользователе, хранящиеся под этим ключом",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Ключ. Пример: должность"
                            },
                            "value": {
                                "type": "string",
                                "description": "Значение. Пример к примеру из key: разработчик"
                            }
                        },
                        "required": [
                            "key",
                            "value"
                        ]
                    }
                },
            },
            "required": ["data"]
        }
    }
]

update_action_function = [
    {
        "name": "update_arbitrary_data",
        "description": "По запросу пользователя обновляет/добавляет произвольные данные о нём",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "description": "Список из пар ключ:значение - данные, которые пользователь просит обновить/добавить",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Ключ для сохранения произвольных данных в json файле"
                            },
                            "value": {
                                "type": "string",
                                "description": "Значение, которое нужно сохранить в json файле под соотвестующим ключом"
                            }
                        },
                        "required": [
                            "key",
                            "value"
                        ]
                    }
                },
            },
            "required": [
                "data",

            ]
        }
    }
]