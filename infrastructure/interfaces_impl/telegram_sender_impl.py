from aiogram import Bot, types
from icecream import ic
from application.telegram.interfaces.telegram_sender_interface import TelegramSenderInterface
from domain.entities.mail import Mail

MAX_CAPTION_LENGTH = 1024

class TelegramMailSenderImpl(TelegramSenderInterface):
    def __init__(self, bot: Bot):
        self.bot = bot

    def __split_message_text_for_caption(self, message_text):
        if len(message_text) > MAX_CAPTION_LENGTH:
            caption_text = message_text[:MAX_CAPTION_LENGTH + 1]
            rest_text = message_text[MAX_CAPTION_LENGTH + 1:len(message_text + 1)]
            return caption_text, rest_text
        return message_text, None
    
    def __get_recipients_ids(self, mail: Mail):
        print(mail.recipients)
        return [user.user_id for user in mail.recipients['known_recipients']]
   
   
    async def __send_message_with_attachment(self, message_text: str, attachment: types.Message, recipients):
        caption_text, rest_message_text = self.__split_message_text_for_caption(message_text)
        for user in recipients:
            if '{}' in message_text:
                #TODO: исправить то, что поля user.first_name и user.last_name равны None
                message_text_formatted = message_text.replace('{}', user.full_name.split()[0])
                caption_text, rest_message_text = self.__split_message_text_for_caption(message_text_formatted)
            if attachment.document:
                await self.bot.send_document(chat_id=user.user_id, document=attachment.document.file_id, caption=caption_text)
            elif attachment.photo:
                await self.bot.send_photo(chat_id=user.user_id, photo=attachment.photo[-1].file_id, caption=caption_text)
            elif attachment.video:
                await self.bot.send_video(chat_id=user.user_id, video=attachment.video.file_id, caption=caption_text)
                print(attachment.video.file_id)
            elif attachment.audio:
                await self.bot.send_audio(chat_id=user.user_id, audio=attachment.audio.file_id, caption=caption_text)
            elif attachment.voice:
                await self.bot.send_voice(chat_id=user.user_id, voice=attachment.voice.file_id, caption=caption_text)
            elif attachment.video_note:
                # video note has no captions so we send whole message after an attachment
                await self.bot.send_video_note(chat_id=user.user_id, video_note=attachment.video_note.file_id)
                await self.bot.send_message(chat_id=user.user_id, text=message_text)
            elif attachment.media_group:
                # same as a video note
                await self.bot.send_media_group(chat_id=user.user_id, media=attachment.video.file_id)
                await self.bot.send_message(chat_id=user.user_id, text=message_text)
            elif attachment.animation:
                await self.bot.send_animation(chat_id=user.user_id, animation=attachment.animation.file_id, caption=caption_text)
            elif attachment.sticker:
                await self.bot.send_sticker(chat_id=user.user_id, sticker=attachment.sticker.file_id)
                await self.bot.send_message(chat_id=user.user_id, text=message_text)

        if rest_message_text is not None:
            await self.bot.send_message(chat_id=user.user_id, text=rest_message_text)
        print("message with attachment sent ")
    async def __send_message_no_attachment(self, message_text, recipients):
        message_text_formatted = message_text
        for user in recipients:
            if '{}' in message_text:
                message_text_formatted = message_text.replace('{}', user.full_name.split()[0])
            await self.bot.send_message(chat_id=user.user_id, text=message_text_formatted)
            print("message with no attachment sent ")

    async def send_message(self, mail: Mail):
        print("send_message called")
        recipients = mail.recipients['known_recipients']
        message_text = f"✉️ Вам письмо!\n\n📌 Тема: {mail.topic}\n\n👤 Отправитель: {mail.author_user.full_name} ({mail.author_user.username})\n\n💬 Cообщение:\n{mail.body}"
        attachment: types.Message = mail.attachment
        try:
            if attachment is not None:
                await self.__send_message_with_attachment(message_text, attachment, recipients)
            else:                
                await self.__send_message_no_attachment(message_text, recipients)
        except Exception as e:
            print(e)
        return None