compose_all_meeting_dates = [
    {
        "name": "compose_meeting_dates",
        "description": "По запросу пользователя составляет встречу/созвон.",
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_date": {
                    "type": "string",
                    "description": "Дата, на которую нужно назначить встречу СТРОГО в формате dd.mm.yyyy. 0, если дата встречи не указана"
                },
                "meeting_time": {
                    "type": "string",
                    "description": "Время встречи СТРОГО в формате HH:MM. 0, если дата не указана. 23:59, если дата указано, но время не указано"
                },
                "remind_time": {
                    "type": "string",
                    "description": "Время, в которое нужно напомнить о встрече . '0', если не указано"
                },
                "remind_date": {
                    "type": "string",
                    "description": "Дата, когда нужно напомнить о встрече СТРОГО в формате dd.mm.yyyy. '0', если не указано."
                }
            },
            "required": [
                "meeting_date",
                "meeting_time",
                "remind_time",
                "remind_date"
            ]
        }
    }
]

compose_all_meeting_participants = [
    {
        "name": "compose_meeting_participants",
        "description": "По запросу пользователя составляет список участников встречи/созвона, а также модератора встречи/созвона.",
        "parameters": {
            "type": "object",
            "properties": {
                "author_name": {
                    "type": "string",
                    "description": "Имя человека, который назначается встречу. '0', если не указано"
                },
                "moderator_name": {
                    "type": "string",
                    "description": "Имя модератора встречи. 0, если модератор не указан."
                },
                "participants_data": {
                    "type": "array",
                    "description": "Список ПРИГЛАШЕННЫХ на встречу/созвон пользователей. [], если пользователи не указаны",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Имя и фамилия (если указана) приглашенного пользователя"
                            },
                            "email": {
                                "type": "string",
                                "description": "Почта приглашенного пользователя. '0', если не указана",
                                "default": "0"
                            },
                            "telegram": {
                                "type": "string",
                                "description": "Юзернейм приглашенного пользователя. '0', если не указан",
                                "default": "0"
                            }
                        },
                        
                        "required": [
                                "name",
                                "email",
                                "telegram"
                            ]
                    }
                },
                "invite_all": {
                    "type": "integer",
                    "description": "1, если пользователь просит пригласить всех участников коллектива/команды. 0, если не просит"
                }
            },
            "required": [
                    "participants_data",
                    "moderator_name",
                    "author_name",
                    "invite_all"
                ]
        }
    }
]

compose_all_meeting_extra_data = [
    {
        "name": "compose_meeting_extra_data",
        "description": "По запросу пользователя составляет дополнительные данные встречи/созвона.",
        "parameters": {
            "type": "object",
            "properties": {
                "link": {
                    "type": "string",
                    "description": "Ссылка на встречу/созвон. 0, если ссылка не указана"
                },
                "invitation_type": {
                    "type": "string",
                    "description": "Куда отправить ссылку на встречу. 'email' - если ссылку нужно отправить на электронную почту, 'telegram' - если ссылку нужно отправить в телеграм. 'telegram', если не указано",
                    "enum": ["email", "telegram"],
                    "default": "telegram"
                },
                "topic": {
                    "type": "string",
                    "description": "Тема встречи/созвона. 0, если тема не указана"
                },
                "duration": {
                    "type": "string",
                    "description": "Продолжительность встречи в минутах. 30, если продолжительность не указана"
                }
            },
            "required": [
                "link",
                "invitation_type",
                "topic",
                "duration"
            ]
        }
    }
]

change_meeting_moderator = [
    {
        "name": "change_meeting_moderator",
        "description": "Функция вызывается, когда нужно получить имя модератора встречи или созвона. 0, если модератор не указан",
        "parameters": {
            "type": "object",
            "properties": {
                "moderator_name": {
                    "type": "string",
                    "description": "Имя модератора встречи. 0, если модератор не указан. "
                }
            },
            "required": [
                "moderator"
            ]
        }
    }
]

change_meeting_topic = [
    {
        "name": "change_meeting_topic",
        "description": "Функция вызывается, когда нужно получить тему встречи или созвона.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Тема встречи/созвона."
                }
            },
            "required": [
                "topic"
            ]
        }
    },
]


change_meeting_duration = [
    {
        "name": "change_meeting_duration",
        "description": "Функция вызывается, когда нужно получить продолжительности встречи или созвона",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {
                    "type": "string",
                    "description": "Продолжительность встречи в минутах."
                }
            },
            "required": [
                    "duration"
                ]
        }
    }
]

change_meeting_link = [
    {
        "name": "change_meeting_link",
        "description": "Функция вызывается, когда нужно получить ссылку на встречу или созвон. 0, если ссылка не указана в сообщение пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "link": {
                    "type": "string",
                    "description": "Ссылка на встречу/созвон. 0, если ссылка не указана"
                }
            },
            "required": [
                "link"
            ]
        }
    },
]

change_meeting_remind_datetime = [
    {
        "name": "change_meeting_remind_datetime",
        "description": "Функция вызывается, когда нужно получить время и дату напоминания о встрече или созвоне. 0, если время напоминания не указано в сообщении пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "remind_time": {
                    "type": "string",
                    "description": "Время, в которое нужно напомнить о встрече СТРОГО в формате HH:MM. 0, если время не указано."
                },
                "remind_date": {
                    "type": "string",
                    "description": "Дата, в которую нужно напомнить о встрече СТРОГО в формате dd.mm.yyyy. 0, если дата не указана."
                }
            },
            "required": [
                "remind_date",
                "remind_time"
            ]
        }
    }
]

change_meeting_datetime = [
    {
        "name": "change_meeting_datetime",
        "description": "Функция вызывается, когда нужно получить дату и время встречи или созвона. 0, если дата встречи не указана в сообщении пользователя",
        "parameters": {
            "type": "object",
            "properties": {
                "meeting_date": {
                    "type": "string",
                    "description": "Дата, на которую нужно назначить встречу СТРОГО в формате dd.mm.yyyy. 0, если дата встречи не указана"
                },
                "meeting_time": {
                    "type": "string",
                    "description": "Время встречи СТРОГО в формате HH:MM. 0, если время не указано"
                }
            },
            "required": [
                "meeting_date",
                "meeting_time"
            ]
        },
    }
]

change_meeting_participants = [
    {
        "name": "change_meeting_participants",
        "description": "По запросу пользователя модифицирует список участников встречи/созвона.",
        "parameters": {
            "type": "object",
            "properties": {
                "participants_data": {
                    "type": "array",
                    "description": "Список ПРИГЛАШЕННЫХ на встречу/созвон пользователей. [], если пользователи не указаны",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Имя и фамилия (если указана) приглашенного пользователя"
                            },
                            "email": {
                                "type": "string",
                                "description": "Почта приглашенного пользователя. '0', если не указана",
                                "default": "0"
                            },
                            "telegram": {
                                "type": "string",
                                "description": "Юзернейм приглашенного пользователя. '0', если не указан",
                                "default": "0"
                            }
                        },
                        "required": [
                                "name",
                                "email",
                                "telegram"
                            ]
                    }
                },
                "invite_all": {
                    "type": "integer",
                    "description": "1, если пользователь попросил пригласить всех участников коллектива/команды. 0, если не попросил!!!"
                }
            },
            "required": [
                    "participants_data",
                    "invite_all"
                ]
        },
    }
]