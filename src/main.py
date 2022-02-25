import wave

import requests
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from vosk import KaldiRecognizer, Model

from bot.voice_recognizer import voice_model
import os,sys
from pydub import AudioSegment

TELEGRAM_API_TOKEN = '5149750371:AAEYOvu-O0jgqHq5PZM3xyvTQ9Cni7T-woc'


def main():
    bot = Bot(token=TELEGRAM_API_TOKEN)
    dp = Dispatcher(bot)

    @dp.message_handler(commands=["start"])
    async def start(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    @dp.message_handler(content_types=['text'])
    async def text_mess(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    @dp.message_handler(content_types=['voice'])
    async def voice_mess(message):
        file_info = await bot.get_file(message.voice.file_id)
        await bot.download_file(file_info.file_path, destination='new.ogg')
        song = AudioSegment.from_ogg('new.ogg')
        song.export("temp.wav", format="wav")
        model = Model('src/bot/voice_recognizer/vosk-model-small-ru-0.22')
        wave_audio_file = wave.open("temp.wav", "r")
        file_recognizer = KaldiRecognizer(model,
                                          wave_audio_file.getframerate())
        print(file_recognizer.Result())
        await bot.send_message(message.chat.id, text=f'Распознан текст:\n'
                                                     f'{file_recognizer.Result()}')

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
