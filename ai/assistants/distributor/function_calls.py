distibutor_func = [
    {
        "name": "get_assistant",
        "description": "Исходя из контекста функция вызывает нужного ассистента",
        "parameters": {
            "type": "object",
            "properties": {
                "assistant_name": {
                    "type": "string",
                    "description": "Имя ассистента, которого нужно вызвать",
                    "enum": ["meeting_assistant", "task_assistant", "mailing_assistant", "talker", 'arbitrary_data_manager', 'no_assistant']
                }
            },
            "required": ["assistant_name"]
        }
    }
]