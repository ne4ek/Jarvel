import torch
import os
from aiogram import types, Bot, Router, F 
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from const import DIRNAME, VOICE_WORDS, TITLE_FOR_SOURCE_TRANSCRIBED_TEXT, MAX_VOICE_DURATION, MIN_MESSAGE_LENGTH_FOR_SUMMARIZE, MAX_SOURCE_TRANSCRIBED_TEXT_LENGTH, MAX_MESSAGE_LENGTH
from ai.summarization_prompts import summarization_prompt
from infrastructure.config.bot_config import bot
from audio_extract import extract_audio
from openai import AsyncOpenAI
from application.messages.custom_errors.duration_error import DurationTooLongError
from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from domain.entities.transcribed_message import TranscribedMessage
from functools import wraps
from domain.entities.tunneling_message import TunnelingMessage
import logging
from icecream import ic
import asyncio
import ffmpeg

class TranscribeTelegramMessage:
    def __init__(self, torch_model, api_key: str, trancriber_model: str, bot: Bot, words_for_transcriber: str, gpt_model: str, gpt_temperature: int, summarizer_prompt: str, repositories: RepositoriesDependencyProviderImplAsync):
        self.client = AsyncOpenAI(api_key=api_key)
        self.trancriber_model = trancriber_model
        self.bot = bot
        self.torch_model = torch_model
        self.words_for_transcriber = words_for_transcriber
        self.gpt_model = gpt_model
        self.gpt_temperature = gpt_temperature
        self.summarizer_prompt = summarizer_prompt
        self.repositories = repositories
        self.user_repository = repositories.get_users_repository()
        self.tunneling_repository = repositories.get_tunneling_repository()
        
    def get_router(self):
        router = Router()
        self.register_callbacks(router)
        return router
    
    def register_callbacks(self, router: Router):
        router.callback_query.register(self.source_transcribed_callback, F.data.startswith("get_source_transcribed_text id"))
        router.callback_query.register(self.short_transcribed_callback, F.data.startswith("get_short_transcribed_text id"))

    async def source_transcribed_callback(self, callback: types.CallbackQuery):
        id = callback.data.split()[-1]
        shorted_text = callback.message.text.split("\n\n")[:2]
        bot_response_message = await self.__get_source_bot_full_message(shorted_text, id)
        await callback.message.edit_text(text=bot_response_message["text"], reply_markup = bot_response_message["keyboard"], parse_mode="HTML")
        
    async def short_transcribed_callback(self, callback: types.CallbackQuery):
        id = callback.data.split()[-1]
        text_list = callback.message.text.split("\n\n")
        short_text = text_list[:2]
        source_text = text_list[-1].replace(TITLE_FOR_SOURCE_TRANSCRIBED_TEXT, "").strip()
        truncated_text = self.__truncate_to_words(source_text)
        bot_response_message = self.__get_short_bot_full_message(short_text, truncated_text, id)
        await callback.message.edit_text(text=bot_response_message["text"], reply_markup = bot_response_message["keyboard"], parse_mode="HTML") 
        
    async def execute(self, message: types.Message):
        if message.voice:
            duration = message.voice.duration
        elif message.video_note:
            duration = message.video_note.duration
        else:
            duration = 200
        if duration > MAX_VOICE_DURATION:
            raise DurationTooLongError(f"Voice/video_note duration is over {MAX_VOICE_DURATION} seconds")
        
        fp_disk = await self.__save_voice_message(message)
        fp_disk_voice_only = self.__get_voice_only(audio_file_path=fp_disk)
        if not fp_disk_voice_only:
            raise ValueError
        
        saved_file = open(fp_disk_voice_only, "rb")
        
        transcription = await self.client.audio.transcriptions.create(
            model=self.trancriber_model,
            file=saved_file,
            response_format="text",
            prompt=self.words_for_transcriber
        )
        return self.__get_trancribed_message_entitiy(transcription, message)
    

    
    def __get_voice_only(self, audio_file_path: str):
        torch.set_num_threads(1)
        
        model, utils = self.torch_model
        (get_speech_timestamps,
        save_audio,
        read_audio,
        _,
        collect_chunks) = utils

        sampling_rate = 16000
        
        wav = read_audio(audio_file_path, sampling_rate=sampling_rate)
        speech_timestamps = get_speech_timestamps(wav, model, sampling_rate=sampling_rate, threshold=0.3)
        fp_disk = os.path.join(DIRNAME, "storage", f"{os.path.basename(audio_file_path)}.wav")
        if speech_timestamps:
            save_audio(fp_disk, collect_chunks(speech_timestamps, wav), sampling_rate=sampling_rate)
            os.remove(fp_disk)
            return audio_file_path
        return

    async def summarize(self, user_text, user: types.User):
        user_db = await self.user_repository.get_by_id(user.id)
        if user_db:
            user_text = f"П ({user_db.full_name}): {user_text}"
        else:
            user_text = f"П ({user.full_name}): {user_text}"
        
        context = [{"role": "system", "content": self.summarizer_prompt},
                       {"role": "user", "content": user_text}]
        response = await self.client.chat.completions.create(
            messages=context,
            model=self.gpt_model,
            temperature=self.gpt_temperature
        )
        response_message = response.choices[0].message
        return response_message.content

    def __get_short_bot_message_keyboard(self, id):
        button_text = "Скрыть"
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, callback_data=f"get_short_transcribed_text id {id}")]])
    
    def __get_source_bot_message_keyboard(self, id):
        keyboard_text = "Показать иходное сообщение" 
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=keyboard_text, callback_data=f"get_source_transcribed_text id {id}")]])

    def __get_short_bot_full_message(self, short_message, truncated_source_text, id):
        bot_message_text = f"<b>{short_message[0]}</b>\n\n{short_message[1]}\n\n{TITLE_FOR_SOURCE_TRANSCRIBED_TEXT}\n{truncated_source_text}..."
        return {"text": bot_message_text, "keyboard": self.__get_source_bot_message_keyboard(id)}
    
    async def __get_source_bot_full_message(self, short_message, id):
        sourse_text_repository = self.repositories.get_transcribed_voice_message_text_repository()
        source_text = await sourse_text_repository.get_text_by_id(int(id))
        bot_message_text = f"<b>{short_message[0]}</b>\n\n{short_message[1]}\n\n{TITLE_FOR_SOURCE_TRANSCRIBED_TEXT}\n{source_text}"
        if len(bot_message_text) > MAX_MESSAGE_LENGTH:
            point_count = 3
            differences = len(bot_message_text) - MAX_MESSAGE_LENGTH - point_count
            truncated_source_text = self.__truncate_to_words(source_text, differences)
            bot_message_text = f"<b>{short_message[0]}</b>\n\n{short_message[1]}\n\n{TITLE_FOR_SOURCE_TRANSCRIBED_TEXT}\n{truncated_source_text}"
        return {"text": bot_message_text, "keyboard": self.__get_short_bot_message_keyboard(id)}
    
    async def get_bot_response_message(self, message, transcribed_message: str):
        summarized_text = await transcribe_message.summarize(transcribed_message, user=message.from_user)
        truncated_source_text = self.__truncate_to_words(transcribed_message, MAX_SOURCE_TRANSCRIBED_TEXT_LENGTH)
        transcribed_voice_message_text_repository = transcribe_message.repositories.get_transcribed_voice_message_text_repository()
        transcribed_voice_message_text_id = await transcribed_voice_message_text_repository.save(transcribed_message)
        return self.__get_short_bot_full_message(summarized_text.split("\n\n")[:2], truncated_source_text, transcribed_voice_message_text_id)

    def __truncate_to_words(self, text, max_length=MAX_SOURCE_TRANSCRIBED_TEXT_LENGTH):
        if len(text) <= max_length:
            return text
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated

    async def __save_voice_message(self, message: types.Message):
        is_voice = isinstance(message.voice, types.Voice)
        is_video_note = isinstance(message.video_note, types.VideoNote)
        is_video_document = isinstance(message.document, types.Document) and message.document.mime_type in ["video/webm", "video/mp4"] 
        is_video_video = isinstance(message.video, types.Video) and message.video.mime_type in ["video/webm", "video/mp4"]
        if is_voice:
            file_id = message.voice.file_id
        elif is_video_note:
            file_id = message.video_note.file_id
        elif is_video_document:
            file_id = message.document.file_id
        elif is_video_video:
            file_id = message.video.file_id
        file = await self.bot.get_file(file_id)
        fp = file.file_path
        if is_voice:
            fp_disk = os.path.join(DIRNAME, "storage", f"{file_id}.ogg")
            await self.bot.download_file(fp, destination=fp_disk)
        elif is_video_note:
            temp = os.path.join(DIRNAME, "storage", f"{file.file_id}.mp4")
            await self.bot.download_file(fp, destination=temp)
            fp_disk = os.path.join(DIRNAME, "storage", f"{file.file_id}.mp3")
            extract_audio(input_path=temp, output_path=fp_disk)
            os.remove(temp)
        elif is_video_document:
            temp = os.path.join(DIRNAME, "storage", f"{file.file_id}.webm") if message.document.mime_type == "video/webm" else os.path.join(DIRNAME, "storage", f"{file.file_id}.mp4")
            await self.bot.download_file(fp, destination=temp)
            fp_disk = os.path.join(DIRNAME, "storage", f"{file.file_id}.mp3")
            ffmpeg.input(temp).output(fp_disk, format='mp3').run(overwrite_output=True, quiet=True)
            os.remove(temp)
        elif is_video_video:
            ic("is_video_video")
            temp = os.path.join(DIRNAME, "storage", f"{file.file_id}.webm") if message.video.mime_type == "video/webm" else os.path.join(DIRNAME, "storage", f"{file.file_id}.mp4")
            await self.bot.download_file(fp, destination=temp)                
            fp_disk = os.path.join(DIRNAME, "storage", f"{file.file_id}.mp3")
            ffmpeg.input(temp).output(fp_disk, format='mp3').run(overwrite_output=True, quiet=True)
            os.remove(temp)    
        else:
            raise ValueError
        return fp_disk

    async def make_simple_send_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage, text: str, reply_markup=None) -> None:
        bot = message.bot
        for tunneling_message_from_db in tunneling_messages_from_db:
            await bot.send_message(chat_id=tunneling_message_from_db.to_chat_id, 
                                    message_thread_id=tunneling_message_from_db.to_topic_id,
                                    text = text, 
                                    reply_markup = reply_markup,
                                    parse_mode = "HTML",
                                   )

    def __get_trancribed_message_entitiy(self, transcription, original_message: types.Message):
        transcribed_message = TranscribedMessage(message_id=original_message.message_id,
                                                 chat=original_message.chat,
                                                 text=transcription,
                                                 bot=original_message.bot,
                                                 date=original_message.date,
                                                 from_user=original_message.from_user,
                                                 reply_to_message=original_message.reply_to_message,
                                                 summarized_text=None,
                                                 original_message=original_message,)
        return transcribed_message
    
model = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                  model='silero_vad',
                                  force_reload=False)


transcribe_message = TranscribeTelegramMessage(torch_model=model,
                                               api_key=os.getenv("GPT_API_KEY"),
                                               trancriber_model="whisper-1",
                                               bot=bot,
                                               words_for_transcriber=VOICE_WORDS,
                                               gpt_model="gpt-4o-mini",
                                               gpt_temperature=0,
                                               summarizer_prompt=summarization_prompt,
                                               repositories=repositroties_dependency_provider_async)

transcribe_message_router = transcribe_message.get_router()

def audio_to_text_converter(handler):
    @wraps(handler)
    async def wrapper(self, message: types.Message, *args, **kwargs):
        is_voice = isinstance(message.voice, types.Voice)
        is_video_note = isinstance(message.video_note, types.VideoNote)
        is_video_document = isinstance(message.document, types.Document) and message.document.mime_type in ["video/webm", "video/mp4"] 
        is_video_video = isinstance(message.video, types.Video) and message.video.mime_type in ["video/webm", "video/mp4"]
        if is_voice or is_video_note or is_video_document or is_video_video:
            finally_message_for_send = {"text": "", "keyboard": None}
            if is_voice:
                duration = message.voice.duration
            elif is_video_note:
                duration = message.video_note.duration
            else:
                duration = 200
            ic(duration)
            state = kwargs.get("state")
            state = await state.get_state() if state else None
            state = None if not state or "empty" in state else state

            if duration > MAX_VOICE_DURATION:
                finally_message_for_send["text"] = "Сообщение слишком длинное"
                await message.reply(finally_message_for_send["text"], parse_mode="HTML")
                tunneling_messages_from_db = await transcribe_message.tunneling_repository.get_any_by_from_info(TunnelingMessage(
                    from_chat_id=message.chat.id,
                    from_topic_id=message.message_thread_id,
                ))
                await transcribe_message.make_simple_send_tunneling(message, tunneling_messages_from_db, text=finally_message_for_send["text"])
                await handler(self, message, *args, **kwargs)
            else:
                try:
                    bot_message = await message.reply("Сообщение обрабатывается...")
                    try:
                        transcribed_message = await transcribe_message.execute(message)
                    except TelegramBadRequest as e:
                        finally_message_for_send["text"] = "Сообщение слишком длинное"
                        await bot_message.edit_text(finally_message_for_send["text"], parse_mode="HTML")
                        ic("Сообщение слишком длинное")
                        return
                    if not state:       
                        if len(transcribed_message.text) < MIN_MESSAGE_LENGTH_FOR_SUMMARIZE:
                            finally_message_for_send["text"] = transcribed_message.text
                        else:
                            bot_response_message = await transcribe_message.get_bot_response_message(message, transcribed_message.text)
                            finally_message_for_send["text"] = bot_response_message["text"]
                            finally_message_for_send["keyboard"] = bot_response_message["keyboard"] 
                    await bot_message.edit_text(text = finally_message_for_send["text"], 
                                                reply_markup = finally_message_for_send["keyboard"],
                                                parse_mode="HTML")
                    tunneling_messages_from_db = await transcribe_message.tunneling_repository.get_any_by_from_info(TunnelingMessage(
                        from_chat_id=message.chat.id,
                        from_topic_id=message.message_thread_id,
                    ))
                    await transcribe_message.make_simple_send_tunneling(message, tunneling_messages_from_db, text=finally_message_for_send["text"], reply_markup=finally_message_for_send["keyboard"])
                    await handler(self, transcribed_message, *args, **kwargs)
                except Exception as e:
                    try:
                        await bot_message.delete()
                        pass
                    except TelegramBadRequest as te:
                        return
                    await handler(self, message, *args, **kwargs)
                    raise e
        else:
            await handler(self, message, *args, **kwargs)
    return wrapper
            