import mimetypes

from aiogram import Bot
from redmail import gmail
from application.email.interfaces.send_email_interface import EmailSenderInterface
import os
from email.message import EmailMessage
from aiosmtplib import SMTP
from const import DIRNAME
from icecream import ic 
import logging
from domain.entities.mail import Mail

class EmailMailSenderImpl(EmailSenderInterface):
    def __init__(self, bot: Bot):
        self.gmail = gmail
        self.bot = bot
        self.username = os.getenv("EMAIL")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.hostname = "smtp.gmail.com"
        self.port = 587
       
    async def send_email(self, mail:Mail):
        known_recipients = mail.recipients['known_recipients']
        topic = mail.topic
        body = mail.body
        attachment = mail.attachment
        not_send_recipients = []
        for user in known_recipients:
            try:
                message = EmailMessage()
                message["From"] = self.username
                message["To"] = user.email
                message["Subject"] = topic
                if '{}' in body:
                    body_formatted = body.replace('{}', user.full_name.split()[0])
                    message.set_content(body_formatted)
                else:
                    message.set_content(body)
                fp_disk = None
                if attachment is not None:
                    if attachment.document:
                        file_id = attachment.document.file_id
                        file = await self.bot.get_file(file_id)
                        file_path = file.file_path
                        file_name = attachment.document.file_name
                        ic(file_name, file_path)

                        ctype, encoding = mimetypes.guess_type(file_path)
                        if ctype is None or encoding is not None:
                            ctype = 'application/octet-stream'
                        maintype, subtype = ctype.split('/', 1)

                        fp_disk = os.path.join(DIRNAME, "storage", f"file_{file_id}.{file_path.split('.')[-1]}")
                        await self.bot.download_file(file_path, fp_disk)
                        with open(fp_disk, "rb") as fp:
                            message.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=file_name)
                    elif attachment.photo:
                        file_id = attachment.photo[-1].file_id
                        file = await self.bot.get_file(file_id)
                        file_path = file.file_path
                        file_name = f"{file_id}.jpeg"

                        ctype, encoding = mimetypes.guess_type(file_path)
                        if ctype is None or encoding is not None:
                            ctype = 'application/octet-stream'
                        maintype, subtype = ctype.split('/', 1)

                        fp_disk = os.path.join(DIRNAME, "storage", f"file_{file_id}.{file_path.split('.')[-1]}")
                        await self.bot.download_file(file_path, fp_disk)
                        with open(fp_disk, "rb") as fp:
                            message.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=file_name)

                async with SMTP(hostname=self.hostname, port=self.port, username=self.username,
                                password=self.password, start_tls=True) as smtp_client:
                    await smtp_client.send_message(message)
                await smtp_client.quit()
                if fp_disk and os.path.exists(fp_disk):
                    os.remove(fp_disk)

            except Exception as e:
                not_send_recipients.append(user.email)
        return None


    async def send_email_sync(self, mail):
        known_recipients = mail.recipients['known_recipients']
        known_recipients_emails = [user.email for user in known_recipients]
        topic = mail.topic
        body = mail.body
        attachment = mail.attachment
        not_send_recipients = []
        for email in known_recipients_emails:
            try:
                if attachment is not None:
                    if attachment.document:
                        file_id = attachment.document.file_id
                        file = await self.bot.get_file(file_id)
                        file_path = file.file_path
                        file_name = attachment.document.file_name
                    elif attachment.photo:
                        file_id = attachment.photo[-1].file_id
                        file = await self.bot.get_file(file_id)
                        file_path = file.file_path
                        file_name = f"{file_id}.jpeg"
                    # добавить остальные виды файлов

                    await self.bot.download_file(file_path, file_name)
                    self.gmail.send(
                        subject=topic,
                        receivers=email,
                        text=body,
                        attachments={file_name:file_path}
                    )
                    if os.path.exists(file_path):
                        os.remove(file_path)
                self.gmail.send(
                    subject=topic,
                    receivers=email,
                    text=body)

            except Exception as e:
                logging.warning(f"Error sending email: {e}")
                not_send_recipients.append(email)
        return None

        # достаем из mail и отправляем. Пройтись по неизвестным пользователям и получить адреса email


