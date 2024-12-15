import torch
import os
from aiogram import types, Bot
from aiogram.exceptions import TelegramBadRequest
from const import DIRNAME, VOICE_WORDS, MAX_MESSAGE_LENGTH, MAX_VOICE_DURATION, MAX_VOICE_DURATION_FOR_SUMMARIZE
from ai.summarization_prompts import summarization_prompt
from infrastructure.config.bot_config import bot
from audio_extract import extract_audio
from openai import AsyncOpenAI
from application.messages.custom_errors.duration_error import DurationTooLongError
from application.providers.repositories_provider import RepositoriesDependencyProvider
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from domain.entities.transcribed_message import TranscribedMessage
from functools import wraps
import logging
from icecream import ic
import asyncio
import ffmpeg

class TranscribeTelegramMessage:
    def __init__(self, torch_model, api_key: str, trancriber_model: str, bot: Bot, words_for_transcriber: str, gpt_model: str, gpt_temperature: int, summarizer_prompt: str, repositories: RepositoriesDependencyProvider):
        self.client = AsyncOpenAI(api_key=api_key)
        self.trancriber_model = trancriber_model
        self.bot = bot
        self.torch_model = torch_model
        self.words_for_transcriber = words_for_transcriber
        self.gpt_model = gpt_model
        self.gpt_temperature = gpt_temperature
        self.summarizer_prompt = summarizer_prompt
        self.user_repository = repositories.get_users_repository()
    
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

    async def summarize(self, message: TranscribedMessage, user: types.User):
        user_db = await self.user_repository.get_by_id(user.id)
        user_text = message.text
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

    def __get_trancribed_message_entitiy(self, transcription, original_message: types.Message):
        transcribed_message = TranscribedMessage(message_id=original_message.message_id,
                                                 chat=original_message.chat,
                                                 text=transcription,
                                                 bot=original_message.bot,
                                                 date=original_message.date,
                                                 from_user=original_message.from_user,
                                                 reply_to_message=original_message.reply_to_message,
                                                 summarized_text=None,
                                                 original_message=original_message)
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

def audio_to_text_converter(handler):
    @wraps(handler)
    async def wrapper(self, message: types.Message, *args, **kwargs):
        is_voice = isinstance(message.voice, types.Voice)
        is_video_note = isinstance(message.video_note, types.VideoNote)
        is_video_document = isinstance(message.document, types.Document) and message.document.mime_type in ["video/webm", "video/mp4"] 
        is_video_video = isinstance(message.video, types.Video) and message.video.mime_type in ["video/webm", "video/mp4"]
        if is_voice or is_video_note or is_video_document or is_video_video:
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
                await message.reply("Сообщение слишком длинное")
                await handler(self, message, *args, **kwargs)
                return
            try:
                bot_message = await message.reply("Сообщение обрабатывается...")
                try:
                    transcribed_message = await transcribe_message.execute(message)
                except TelegramBadRequest as e:
                    if is_voice:
                        await bot_message.edit_text("Голосовое сообщение слишком длинное")
                    else:
                        await bot_message.edit_text("Видео слишком длинное")
                    ic(str(e))
                    return
                if not state:       
                    if duration < MAX_VOICE_DURATION_FOR_SUMMARIZE:
                        await bot_message.edit_text("Расшифрованное сообщение:\n\n" + transcribed_message.text)
                    else:
                        summarized_text = await transcribe_message.summarize(transcribed_message, user=message.from_user)
                        bot_message_text = f"Суммаризованное сообщение:\n\n{summarized_text}\n\nРасшифрованное сообщение:\n\n{transcribed_message.text}"
                        if len(bot_message_text) < MAX_MESSAGE_LENGTH:
                            await bot_message.edit_text(bot_message_text)
                        else:
                            await bot_message.delete()
                            bot_messages_text = (bot_message_text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(bot_message_text), MAX_MESSAGE_LENGTH))
                            for bot_message_text_splited in bot_messages_text:
                                await message.reply(bot_message_text_splited)
                await handler(self, transcribed_message, *args, **kwargs)
            except Exception as e:
                try:
                    await bot_message.edit_text("Речь не распознана")
                except TelegramBadRequest as te:
                    return
                await handler(self, message, *args, **kwargs)
                raise e
        else:
            await handler(self, message, *args, **kwargs)
    return wrapper
            