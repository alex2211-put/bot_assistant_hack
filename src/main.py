import wave

import requests
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from bot.voice_recognizer import voice_model

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
        # wave_audio_file = wave.open('new.ogg', "rb")
        # print(downloaded_file)
        # with open(f'{message.chat.id}.ogg', 'wb') as new_file:
        #     downloaded_file.write(new_file)
            # new_file.write(downloaded_file)
        model = voice_model.LanguageModel()
        await bot.send_message(message.chat.id, text=f'Распознан текст:\n'
                                                     f'{model.get_text_from_stream(wave.open("new.ogg", "rb").get_frames())}')

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
