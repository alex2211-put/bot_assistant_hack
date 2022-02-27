import requests
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from bot.voice_recognizer import voice_model
from bot.helpers import read_yaml


# TODO: подумать как сохранять инфу о пользователях - о каком проекте
#  они пишут и к какому имеют отношения

def main():
    bot = Bot(token=read_yaml.get_token_tg())
    dp = Dispatcher(bot)

    @dp.message_handler(commands=["start"])
    async def start(message):
        await bot.send_message(message.chat.id, text=f'Пришел объект {message}')

    @dp.message_handler(
        content_types=['video', 'photo', 'document', 'audio', 'location'],
    )
    async def content_mess(message):
        # TODO: сохраняем к проекту
        await bot.send_message(message.chat.id, text=f'Пришел контент {message}')

    @dp.message_handler(content_types=['voice'])
    async def voice_mess(message):
        # TODO: на основе того, что распознали делаем что-то
        session = requests.session()
        text_from_voice = await voice_model.request2text(
            message.voice.file_id,
            session,
        )
        await bot.send_message(message.chat.id, text=f'Распознан текст:\n'
                                                     f'{text_from_voice}')

    @dp.message_handler(commands=["add"])
    async def add_project(message):
        # TODO: сохраняем в бд новый проект по его хэшу.
        #  Добавим машину состояний
        # dbConnection = dbConnection()
        # dbConnection.add_project(message)
        pass

    @dp.message_handler(commands=["all"])
    async def get_active_projects(message):
        # TODO: возвращать только те проекты, к которым имеет отношение user
        # dbConnection = dbConnection()
        # all_projects = dbConnection.get_all_projects_for_user()
        # await bot.send_message(message.chat.id, text=f'Доступные проекты:\n' +
        # '\n'.join(all_projects))
        pass

    @dp.message_handler(commands=["select"])
    async def select_project(message):
        # TODO: меняем в машине состояний или контексте проект,
        #  на котором сейчас пользователь
        pass

    @dp.message_handler(commands=["get"])
    async def get_messages_for_project(message):
        # TODO: в машине состояний меняем состояние и закидываем на выбор того,
        #  какие сообщения поучить / сколько и т. д.
        pass

    @dp.message_handler(commands=["archive"])
    async def delete_project(message):
        # TODO: убираем проект в архив - из бд не удаляем,
        #  но перестаем показывать его в активных
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)
        pass

    @dp.message_handler(commands=["all_with_archive"])
    async def get_all_projects_vs_archive(message):
        # TODO: возвращаем все проекты - даже архивированные
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)
        pass

    @dp.message_handler(content_types=['text'])
    async def text_mess(message):
        # TODO: если он сейчас в проекте, то его сообщение закидываем в бд
        await bot.send_message(message.chat.id, text=f'Пришел текст {message}')

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
