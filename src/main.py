import requests
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from bot.voice_recognizer import voice_model
from bot.helpers import read_yaml


def main():
    bot = Bot(token=read_yaml.get_token_tg())
    dp = Dispatcher(bot)

    @dp.message_handler(commands=["start"])
    async def start(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    @dp.message_handler(content_types=['text'])
    async def text_mess(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    @dp.message_handler(content_types=['voice'])
    async def voice_mess(message):
        session = requests.session()
        text_from_voice = await voice_model.request2text(
            message.voice.file_id,
            session,
        )
        await bot.send_message(message.chat.id, text=f'Распознан текст:\n'
                                                     f'{text_from_voice}')
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
