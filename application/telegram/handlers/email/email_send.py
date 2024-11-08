from redmail import gmail
import os
from pathlib import Path

tag = ""


# async def compose_email(args):
#     """
#     Функция собирает сообщение, которое нужно отправить по email
#
#     :param dict args: Аргументы, из которых собирается письмо
#
#     :return: None
#     """
#     from app.utils.bot_init import bot
#
#     names = ", ".join(args.get("names"))
#     text = args.get("text")
#     company = args.get("company")
#     users = company.get("users")
#     sender = users.get(args.get("sender"))
#     message = args.get("message")
#
#     full_names = await get_full_name(names)
#     users = [users[user] for user in users if users[user].get("name") in full_names]
#     validation_message = f"Отправитель: {sender.get('name')}\n\n"
#     validation_message += "Получатели:"
#     for user in users:
#         validation_message += " " + user.get("name") + f"({user.get('email')})"
#     validation_message += f"\n\nПисьмо:\n {text}"
#     await bot.send_message(
#         chat_id=message.chat.id,
#         text=validation_message,
#         reply_to_message_id=message.message_id,
#     )


# def send_email(args):
#     """
#     Function sends an email message
#
#     :param dict args: Arguments used for sending the email
#
#     :return: None
#     """
#
#     sender = args.get("sender_name")
#     emails = args.get("emails")
#     message = args.get("composed_message")
#     subject = args.get("subject")
#
#     message = (
#         f"Здравствуйте! Вам поступило новое сообщение от {sender}.\n\n"
#         + message
#         + "\n\n"
#         + "//Письмо отправлено с помощью telegram-бота @Jarvel_bot"
#     )
#     gmail.username = os.getenv("JARVEL_EMAIL")
#     gmail.password = os.getenv("JARVEL_EMAIL_PASSWORD")
#     gmail.send(subject=subject, receivers=emails, text=message)


def send_email(emails: list, topic: str, text: str, attachment_paths: str | list[str]):
    """
    Function sends an email message

    :param list emails: Arguments used for sending the email
    :param str topic: Topic of the message
    :param str text: Text of the message
    :param str|list[str] attachment_paths: Путь/Список путей к файлам, которые нужно прикрепить
    :return: None
    """
    gmail.username = os.getenv("JARVEL_EMAIL")
    gmail.password = os.getenv("JARVEL_EMAIL_PASSWORD")
    
    if isinstance(attachment_paths, str):
        
        gmail.send(receivers=emails, subject=topic, text=text,
                   attachments={attachment_paths.split('/')[-1]: Path(attachment_paths)})

    elif isinstance(attachment_paths, list):
        
        gmail.send(receivers=emails, subject=topic, text=text,
                   attachments_pat={attachment_path: attachment_path.split('/')[-1]
                                for attachment_path in attachment_paths})
