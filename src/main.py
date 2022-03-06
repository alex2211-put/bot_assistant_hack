import requests
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram import executor
from bot.voice_recognizer import voice_model
from bot.helpers import read_yaml


# think about how to save information about users -
# what project they write about and what they have to do with


def main():
    bot = Bot(token=read_yaml.get_token_tg())
    dispatcher = Dispatcher(bot)

    @dispatcher.message_handler(commands=['start'])
    async def start(message):
        await bot.send_message(
            message.chat.id, text=f'Пришел объект {message}'
        )

    @dispatcher.message_handler(
        content_types=['video', 'photo', 'document', 'audio', 'location'],
    )
    async def content_mess(message):
        # TODO: save to the project
        await bot.send_message(
            message.chat.id, text=f'Пришел контент {message}'
        )

    @dispatcher.message_handler(content_types=['voice'])
    async def voice_mess(message):
        # TODO: based on what we have recognized, do something
        session = requests.session()
        text_from_voice = await voice_model.request2text(
            message.voice.file_id,
            session,
        )
        await bot.send_message(
            message.chat.id, text=f'Распознан текст:\n' f'{text_from_voice}'
        )

    @dispatcher.message_handler(commands=['add'])
    async def add_project(message):  # pylint: disable=unused-argument
        # TODO: save a new project in the database by its hash.
        #  Add a state machine
        # dbConnection = dbConnection()
        # dbConnection.add_project(message)
        pass

    @dispatcher.message_handler(commands=['all'])
    async def get_active_projects(message):  # pylint: disable=unused-argument
        # TODO: return only those projects that the user is related to
        # dbConnection = dbConnection()
        # all_projects = dbConnection.get_all_projects_for_user()
        # await bot.send_message(message.chat.id, text=f'Доступные проекты:\n'
        # + '\n'.join(all_projects))
        pass

    @dispatcher.message_handler(commands=['select'])
    async def select_project(message):  # pylint: disable=unused-argument
        # TODO: change the project in the state machine or context,
        #  which the user is currently on
        pass

    @dispatcher.message_handler(commands=['get'])
    # pylint: disable=unused-argument
    async def get_messages_for_project(message):
        # TODO: in the state machine change the state and throw it
        #  to the choice of, which messages to receive / how many, etc.
        pass

    @dispatcher.message_handler(commands=['archive'])
    async def delete_project(message):  # pylint: disable=unused-argument
        # TODO: remove the project to the archive - we do not delete it
        #  from the database, but we stop showing it in active
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)
        pass

    @dispatcher.message_handler(commands=['all_with_archive'])
    # pylint: disable=unused-argument
    async def get_all_projects_vs_archive(message):
        # TODO: return all projects - even archived ones
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)
        pass

    @dispatcher.message_handler(content_types=['text'])
    async def text_mess(message):
        # TODO: if it is currently in the project,
        #  throw his message into the database
        await bot.send_message(message.chat.id, text=f'Пришел текст {message}')

    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
