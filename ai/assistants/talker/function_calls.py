get_talker_type = [
    {
        "name": "get_talker_type",
        "description": "Определяет, нужен ли ассистенту доступ в интернет.",
        "parameters": {
            "type": "object",
            "properties": {
                "talker_type": {
                    "type": "string",
                    "description": "Тип ассистента: 'offline' - без интернета, 'online' - с интернетом.",
                    "enum": ["offline", "online"]
                }  
            },
            "required": ["talker_type"]
        }
    }
]