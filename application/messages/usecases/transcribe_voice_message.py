import torch
import os
from typing import Union
from aiogram import types, Bot
from const import DIRNAME, MAX_VOICE_DURATION
from audio_extract import extract_audio
from openai import AsyncOpenAI
from application.messages.custom_errors.duration_error import DurationTooLongError
from domain.entities.transcribed_message import TranscribedMessage

class TranscribeTelegramMessage:
    def __init__(self, torch_model, api_key: str, gpt_model: str, bot: Bot, prompt: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.gpt_model = gpt_model
        self.bot = bot
        self.torch_model = torch_model
        self.prompt = prompt
    
    async def execute(self, message: types.Message):
        if message.voice:
            duration = message.voice.duration
        elif message.video_note:
            duration = message.video_note.duration
        if duration > MAX_VOICE_DURATION:
            raise DurationTooLongError(f"Voice/video_note duration is over {MAX_VOICE_DURATION} seconds")
        
        fp_disk = await self.__save_voice_message(message)
        fp_disk_voice_only = self.__get_voice_only(audio_file_path=fp_disk)
        if not fp_disk_voice_only:
            raise ValueError
        
        saved_file = open(fp_disk_voice_only, "rb")
        
        transcription = await self.client.audio.transcriptions.create(
            model=self.gpt_model,
            file=saved_file,
            response_format="text",
            prompt=self.prompt
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
            return audio_file_path
        return

    async def __save_voice_message(self, message: types.Message):
        if message.voice:
            file_id = message.voice.file_id
        elif message.video_note:
            file_id = message.video_note.file_id
        file = await self.bot.get_file(file_id)
        fp = file.file_path
        if isinstance(message.voice, types.Voice):
            fp_disk = os.path.join(DIRNAME, "storage", f"{file_id}.ogg")
            await self.bot.download_file(fp, destination=fp_disk)
        elif isinstance(message.video_note, types.VideoNote):
            temp = os.path.join(DIRNAME, "storage", f"{file.file_id}.mp4")
            await self.bot.download_file(fp, destination=temp)
            fp_disk = os.path.join(DIRNAME, "storage", f"{file.file_id}.mp3")
            extract_audio(input_path=temp, output_path=fp_disk)
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
                                                 summarized_text=None)
        return transcribed_message