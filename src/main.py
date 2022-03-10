import datetime

import requests
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from bot.voice_recognizer import voice_model
from bot.helpers import read_yaml
import logging

# TODO: think about how to save information about users -
#  what project they write about and what they have to do with

logger = logging.getLogger(__name__)


def main():
    bot = Bot(token=read_yaml.get_token_tg())
    dp = Dispatcher(bot)
    logging.basicConfig(
        filename='main.log',
        level=logging.DEBUG,
        format='%(asctime)s %(name)-30s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    @dp.message_handler(commands=["start"])
    async def start(message):
        logger.info('Get /start command %s', message)
        await bot.send_message(
            message.chat.id, text=f'Пришел объект {message}',
        )

    @dp.message_handler(
        content_types=['video', 'photo', 'document', 'audio', 'location'],
    )
    async def content_mess(message):
        # TODO: save to the project
        logger.info('Get content message %s', message)
        await bot.send_message(
            message.chat.id, text=f'Пришел контент {message}',
        )

    @dp.message_handler(content_types=['voice'])
    async def voice_mess(message):
        # TODO: based on what we have recognized, do something
        logger.info('Get voice message %s', message)
        session = requests.session()
        text_from_voice = await voice_model.request2text(
            message.voice.file_id,
            session,
        )
        logger.info('recognize text from voice: %s', text_from_voice)
        await bot.send_message(message.chat.id, text=f'Распознан текст:\n'
                                                     f'{text_from_voice}')

    @dp.message_handler(commands=["add"])
    async def add_project(message):
        logger.info('Get /add command %s', message)
        # TODO: save a new project in the database by its hash.
        #  Add a state machine
        # dbConnection = dbConnection()
        # dbConnection.add_project(message)

    @dp.message_handler(commands=["all"])
    async def get_active_projects(message):
        logger.info('Get /all command %s', message)
        # TODO: return only those projects that the user is related to
        # dbConnection = dbConnection()
        # all_projects = dbConnection.get_all_projects_for_user()
        # await bot.send_message(message.chat.id, text=f'Доступные проекты:\n' +
        # '\n'.join(all_projects))

    @dp.message_handler(commands=["select"])
    async def select_project(message):
        logger.info('Get /select command %s', message)
        # TODO: change the project in the state machine or context,
        #  which the user is currently on

    @dp.message_handler(commands=["get"])
    async def get_messages_for_project(message):
        logger.info('Get /get command %s', message)
        # TODO: in the state machine change the state and throw it
        #  to the choice of, which messages to receive / how many, etc.

    @dp.message_handler(commands=["archive"])
    async def delete_project(message):
        logger.info('Get /archive command %s', message)
        # TODO: remove the project to the archive - we do not delete it
        #  from the database, but we stop showing it in active
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)

    @dp.message_handler(commands=["all_with_archive"])
    async def get_all_projects_vs_archive(message):
        logger.info('Get /all_with_archive command %s', message)
        # TODO: return all projects - even archived ones
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)

    @dp.message_handler(content_types=['text'])
    async def text_mess(message):
        logger.info('Get text message %s', message)
        # TODO: if it is currently in the project,
        #  throw his message into the database
        await bot.send_message(message.chat.id, text=f'Пришел текст {message}')

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
