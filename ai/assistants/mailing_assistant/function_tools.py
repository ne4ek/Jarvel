extract_mail_data = [
    {
        "name": "extract_mail_data",
        "description": "По запросу пользователя функция формирует письмо для рассылки",
        "parameters": {
            "type": "object",
            "properties": {
                "mail_author_name": {
                    "type": "string",
                    "description": "Автор письма. Отправитель запроса по умолчанию"
                },
                "mail_body": {
                    "type": "string",
                    "description": "Тело письма. '0', если не указано",
                    "default": "0"
                },
                "mail_topic": {
                    "type": "string",
                    "description": "Тема письма. '0', если тело письма не указано",
                    "default": "0"
                },
                "recipients": {
                    "type": "array",
                    "description": "Информация о получателях письма. Информация должна включать в себя: имя получателя, телеграм получателя (если указан), почта получателя (если указана)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Имя и фамилия (если указана) получателя"
                            },
                            "email": {
                                "type": "string",
                                "description": "Почта получателя. '0', если не указана",
                                "default": "0"
                            },
                            "telegram": {
                                "type": "string",
                                "description": "Юзернейм получателя в телеграмме. '0', если не указан",
                                "default": "0"
                            }
                        },
                        "required": ["name", "email", "telegram"]
                    }
                },
                "contact_type": {
                    "type": "string",
                    "description": "Способ отправки письма. 'telegram' по умолчанию. 'email', если пользователь указал чью-то почту",
                    "enum": ["telegram", "email"],
                    "default": "telegram"
                },
                "sending_delay": {
                    "type": "integer",
                    "description": "Задержка перед отправкой письма в минутах. 1 минута по умолчанию",
                    "default": 1
                }
            },
            "required": [
                "mail_author",
                "mail_body",
                "mail_topic",
                "recipients",
                "contact_type",
                "sending_delay"
            ]
        }
    }
]

change_mail_author = [
    {
        "name": "change_mail_author",
        "description": "Изменяет автора рассылки по просьбе пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "mail_author_name": {
                    "type": "string",
                    "description": "Новый автор рассылки"
                }
            },
            "required": [
                "mail_author_name"
            ]
        }
    }
]

change_mail_body = [
    {
        "name": "change_mail_body",
        "description": "Изменяет текст письма, а также тему письма (при необходимости)",
        "parameters": {
            "type": "object",
            "properties": {
                "mail_body": {
                        "type": "string",
                        "description": "Тело письма. '0', если не указано",
                        "default": "0"
                    },
                "mail_topic": {
                        "type": "string",
                        "description": "Тема письма. '0', если тело письма не указано",
                        "default": "0"
                    },
            },
            "required": [
                "mail_body",
                "mail_topic"
            ]
        }
    }
]

change_mail_topic = [
    {
        "name": "change_mail_topic",
        "description": "Изменяет тему письма",
        "parameters": {
            "type": "object",
            "properties": {
                "mail_topic": {
                            "type": "string",
                            "description": "Тема письма. '0', если тело письма не указано",
                            "default": "0"
                        }
            }
        },
        "required": [
            "mail_topic"
        ]
    }
]

change_mail_recipients = [
    {
        "name": "change_mail_recipients",
        "description": "Изменяет получателей письма",
        "parameters": {
            "type": "object",
            "properties": {
                "recipients": {
                        "type": "array",
                        "description": "Информация о получателях письма. Информация должна включать в себя: имя получателя, телеграм получателя (если указан), почта получателя (если указана)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Имя и фамилия (если указана) получателя"
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Почта получателя. '0', если не указана",
                                    "default": "0"
                                },
                                "telegram": {
                                    "type": "string",
                                    "description": "Юзернейм получателя в телеграмме. '0', если не указан",
                                    "default": "0"
                                }
                            },
                        "required": ["name", "email", "telegram"]
                    }
                }
            },
            "required": ["recipients"]
        }
    }
]

change_mail_send_delay = [
    {
        "name": "change_mail_send_delay",
        "description": "Изменяет время задержки перед отправкой письма в минутах по просьбе пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "sending_delay": {
                    "type": "integer",
                    "description": "Новое время задержки перед отправкой письма в минутах",
                    "default": 1
                }
            },
            "required": [
                "sending_delay"
            ]
        }
    }
]
