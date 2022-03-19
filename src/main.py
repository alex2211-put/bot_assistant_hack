import collections
import logging
import sys

import requests

from aiogram import Bot, types
from aiogram import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import BotCommand

from bot.voice_recognizer import voice_model
from bot.helpers import customer_funcs, project_funcs
from bot.helpers import owner_funcs
from bot.helpers import read_yaml
from bot.helpers import state_machine

# TODO: think about how to save information about users -
#  what project they write about and what they have to do with

logger = logging.getLogger(__name__)
owners = [853881966]
last_project_info = {}
person_states = {}
messages_to_delete = []
available_project_for_customer = collections.defaultdict(set)
available_project_for_owner = collections.defaultdict(set)
projects_info = collections.defaultdict(dict)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
    ]
    await bot.set_my_commands(commands)


def main():
    bot = Bot(token=read_yaml.get_token_tg())
    dispatcher = Dispatcher(bot)
    logging.basicConfig(
        filename='main.log',
        level=logging.DEBUG,
        format='%(asctime)s %(name)-30s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    @dispatcher.message_handler(commands=['start'])
    async def start(message):
        await set_commands(bot)
        logger.info('Get /start command %s', message)
        if message['from'].id in owners:
            await owner_funcs.start_func(bot, message)
        else:
            await customer_funcs.start_func()
        await bot.delete_message(message.chat.id, message.message_id)

    @dispatcher.message_handler(
        content_types=['video', 'photo', 'document', 'audio', 'location'],
    )
    async def content_mess(message):
        # TODO: save to the project
        logger.info('Get content message %s', message)
        await bot.send_message(
            message.chat.id,
            text=f'Пришел контент {message}',
        )

    @dispatcher.message_handler(content_types=['voice'])
    async def voice_mess(message):
        # TODO: based on what we have recognized, do something
        logger.info('Get voice message %s', message)
        session = requests.session()
        text_from_voice = await voice_model.request2text(
            message.voice.file_id,
            session,
        )
        logger.info('recognize text from voice: %s', text_from_voice)
        await bot.send_message(
            message.chat.id, text=f'Распознан текст:\n' f'{text_from_voice}'
        )

    @dispatcher.message_handler(commands=['add'])
    async def add_project(message):
        logger.info('Get /add command %s', message)
        # TODO: save a new project in the database by its hash.
        #  Add a state machine
        # dbConnection = dbConnection()
        # dbConnection.add_project(message)

    @dispatcher.message_handler(commands=['all'])
    async def get_active_projects(message):
        logger.info('Get /all command %s', message)
        # TODO: return only those projects that the user is related to
        # dbConnection = dbConnection()
        # all_projects = dbConnection.get_all_projects_for_user()
        # await bot.send_message(message.chat.id, text=f'Доступные проекты:\n'
        # '\n'.join(all_projects))

    @dispatcher.message_handler(commands=['select'])
    async def select_project(message):
        logger.info('Get /select command %s', message)
        # TODO: change the project in the state machine or context,
        #  which the user is currently on

    @dispatcher.message_handler(commands=['get'])
    # pylint: disable=unused-argument
    async def get_messages_for_project(message):
        logger.info('Get /get command %s', message)
        # TODO: in the state machine change the state and throw it
        #  to the choice of, which messages to receive / how many, etc.

    @dispatcher.message_handler(commands=['archive'])
    async def delete_project(message):
        logger.info('Get /archive command %s', message)
        # TODO: remove the project to the archive - we do not delete it
        #  from the database, but we stop showing it in active
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)

    @dispatcher.message_handler(commands=['all_with_archive'])
    async def get_all_projects_vs_archive(message):
        logger.info('Get /all_with_archive command %s', message)
        # TODO: return all projects - even archived ones
        # dbConnection = dbConnection()
        # dbConnection.archive_project(project)

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.PROJECT_NAME
        )
    )
    async def set_project_name(message):
        logger.info('Get text message %s', message)
        last_project_info['name'] = message.text
        last_project_info['id'] = id(last_project_info['name'])
        person_states[message.from_user.id] = \
            state_machine.ProjectStates.PROJECT_DESCRIPTION
        send_message = await bot.send_message(
            message.chat.id, text='Enter description of project',
        )
        messages_to_delete.extend(
            [message.message_id, send_message.message_id]
        )

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.PROJECT_DESCRIPTION
        )
    )
    async def set_project_description(message):
        logger.info('Get text message %s', message)
        last_project_info['description'] = message.text
        person_states[message.from_user.id] = \
            state_machine.ProjectStates.PROJECT_RESPONSIBLE
        send_message = await bot.send_message(
            message.chat.id,
            text='Enter the responsible people separated by a space.\n'
                 'For example: @person1 @person2',
        )
        messages_to_delete.extend(
            [message.message_id, send_message.message_id]
        )

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.PROJECT_RESPONSIBLE
        )
    )
    async def set_project_responsible(message):
        logger.info('Get text message %s', message)
        last_project_info['responsible'] = message.text
        person_states[message.from_user.id] = \
            state_machine.ProjectStates.PROJECT_MAIN_MESSAGE
        send_message = await bot.send_message(
            message.chat.id,
            text='Enter the message that each recipient will see',
        )
        messages_to_delete.extend(
            [message.message_id, send_message.message_id]
        )

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.PROJECT_MAIN_MESSAGE
        )
    )
    async def set_project_main_message(message):
        logger.info('Get text message %s', message)
        last_project_info['main_message'] = message.text
        person_states[message.from_user.id] = \
            state_machine.ProjectStates.PROJECT_RECIPIENTS
        send_message = await bot.send_message(
            message.chat.id,
            text='Enter the recipients people separated by a space',
        )
        messages_to_delete.extend(
            [message.message_id, send_message.message_id]
        )

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.PROJECT_RECIPIENTS
        )
    )
    async def set_project_recipients(message):
        logger.info('Get text message %s', message)
        last_project_info['recipients'] = message.text
        await owner_funcs.do_work_after_collecting_data(
            bot, last_project_info, messages_to_delete, message.chat.id,
        )
        project_funcs.save_project_info(
            last_project_info=last_project_info,
            available_project_for_customer=available_project_for_customer,
            available_project_for_owner=available_project_for_owner,
            projects_info=projects_info,
        )
        available_project_for_owner[message['from'].username].add(
            last_project_info['id']
        )
        await bot.delete_message(message.chat.id, message.message_id)
        messages_to_delete.clear()

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'projectId')
    async def get_project_options(call):
        username = call['from'].username
        if username in available_project_for_owner.keys():
            await owner_funcs.get_project_options(bot, call)
        else:
            pass

    @dispatcher.callback_query_handler(lambda call: True)
    async def callback_inline(call):
        if call.data == 'shutdown':
            # TODO: save everything into db
            sys.exit(0)
        elif call.data == 'new_project':
            last_project_info['start_message'] = call.message
            await owner_funcs.create_project(
                bot, call.message.chat.id, person_states, messages_to_delete
            )
        elif call.data == 'to_main_owner_page':
            await owner_funcs.main_page(bot, call)
        elif call.data == 'available_projects':
            username = call['from'].username
            if username in available_project_for_owner.keys():
                await owner_funcs.show_available_projects(
                    bot,
                    call,
                    available_project_for_owner[username],
                    projects_info,
                )
            elif username in available_project_for_customer.keys():
                pass
            else:
                key = types.InlineKeyboardMarkup()
                but_1 = types.InlineKeyboardButton(
                    text='🔙',
                    callback_data='to_main_owner_page',
                )
                key.add(but_1)
                await bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text='No projects available',
                    reply_markup=key,
                )

    @dispatcher.message_handler(content_types=['text'])
    async def text_mess(message):
        logger.info('Get text message %s', message)
        # TODO: if it is currently in the project,
        #  throw his message into the database
        await bot.send_message(message.chat.id, text=f'Пришел текст {message}')

    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
