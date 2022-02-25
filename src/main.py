from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor


def main():
    bot = Bot(token='5149750371:AAEYOvu-O0jgqHq5PZM3xyvTQ9Cni7T-woc')
    dp = Dispatcher(bot)

    @dp.message_handler(commands=["start"])
    async def start(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    @dp.message_handler(content_types=['text'])
    async def text_mess(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
    print('hi')
