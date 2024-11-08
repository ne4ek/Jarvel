mailing_confirmation_message = """
Автор письма: {}
Получатели: {}
Тема:{}
Содержание: 
{}

Платформа(куда отправить): {}
Вложенные файлы: {}
Отправить с задержкой: {}

Подтвердите правильность ввода данных, для сохранения письма
"""

mailing_summary_in_list = """
<b>{topic}</b>
Автор: {user}
Получатели: {resipients}
----------------------------------
"""


mailing_summary_one = """
Автор письма: {author} ({author_usermane})
Получатели: {recipients} ({recipients_username})
Тема {topic}
Содержание: {body}
Платформа(куда отправить): {contact_type}
Вложенные файлы: {attachment}
Отправить с задержкой: {send_delay}
"""