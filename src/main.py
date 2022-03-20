import collections
import logging
import sys

import requests

from aiogram import Bot, types
from aiogram import executor
from aiogram.dispatcher import Dispatcher
from aiogram.types import BotCommand

from DB import read_service
from DB.DB_management import DBManagement
from bot.voice_recognizer import voice_model
from bot.helpers import customer_funcs, project_funcs
from bot.helpers import owner_funcs
from bot.helpers import read_yaml
from bot.helpers import state_machine

# TODO: think about how to save information about users -
#  what project they write about and what they have to do with

logger = logging.getLogger(__name__)
owners = read_service.get_owners()
last_project_info = collections.defaultdict(dict)
person_states = collections.defaultdict()
messages_to_delete = []
available_project_for_customer = collections.defaultdict(set)
available_project_for_owner = collections.defaultdict(set)
projects_info = collections.defaultdict(dict)
message_map = collections.defaultdict(dict)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
    ]
    await bot.set_my_commands(commands)


def main():
    bot = Bot(token=read_yaml.get_token_tg())
    dispatcher = Dispatcher(bot)
    data_base = DBManagement()
    for doc in data_base.current_DB['projects_info'].find():
        projects_info[doc['id']] = {
            'name': doc['name'],
            'main_message': doc['main_message'],
            'recipients': doc['recipients'].split(),
            'responsible': doc['responsible'].split(),
            'description': doc['description'],
        }
        for responsible in doc['responsible'].split():
            available_project_for_owner[responsible].add(doc['id'])
        for recipient in doc['recipients'].split():
            available_project_for_customer[recipient].add(doc['id'])
    logging.basicConfig(
        filename='main.log',
        level=logging.DEBUG,
        format='%(asctime)s %(name)-30s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    @dispatcher.message_handler(commands=['start'])
    async def start(message):
        person_states[message.from_user.id] = None
        await set_commands(bot)
        logger.info('Get /start command %s', message)
        if message['from'].username in owners:
            await owner_funcs.start_func(bot, message)
        elif message['from'].username in available_project_for_owner.keys():
            await owner_funcs.start_manager(bot, message)
        else:
            await customer_funcs.start_func(
                bot, message,
                available_project_for_customer[message['from'].username],
                projects_info)
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

    @dispatcher.message_handler(
        lambda message: (
                person_states[message['from'].id] ==
                state_machine.ProjectStates.PROJECT_NAME
        )
    )
    async def set_project_name(message):
        logger.info('Get text message %s', message)
        last_project_info[message.from_user.id]['name'] = message.text
        last_project_info[message.from_user.id]['id'] = id(
            last_project_info[message.from_user.id]['name'])
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
        last_project_info[message.from_user.id]['description'] = message.text
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
        last_project_info[message.from_user.id]['responsible'] = message.text
        person_states[message.from_user.id] = \
            state_machine.ProjectStates.PROJECT_MAIN_MESSAGE
        send_message = await bot.send_message(
            message.chat.id,
            text='Enter the message that each recipient will see',
        )
        last_project_info[message.from_user.id][
            'responsible'] += ' ' + message.from_user.username
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
        last_project_info[message.from_user.id]['main_message'] = message.text
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
        last_project_info[message.from_user.id][
            'recipients'] = message.text
        await owner_funcs.do_work_after_collecting_data(
            bot, last_project_info[message.from_user.id], messages_to_delete,
            message.chat.id,
        )
        project_funcs.save_project_info(
            last_project_info=last_project_info[message.from_user.id],
            available_project_for_customer=available_project_for_customer,
            available_project_for_owner=available_project_for_owner,
            projects_info=projects_info,
        )
        available_project_for_owner[message['from'].username].add(
            last_project_info[message.from_user.id]['id']
        )
        await bot.delete_message(message.chat.id, message.message_id)
        messages_to_delete.clear()
        person_states[message.from_user.id] = None

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.ADD_RECIPIENTS
        )
    )
    async def set_project_main_message(message):
        project_id = int(last_project_info[message.from_user.id]['id'])
        projects_info[project_id][
            'recipients'].extend(message.text.split())
        for recip in message.text.split():
            available_project_for_customer[recip].add(project_id)
        person_states[message.from_user.id] = None
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addRecip_' +
                                                         str(project_id))
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeRec_' +
                                                         str(project_id))
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='projectId_' +
                                                         str(project_id))
        key.add(but_1, but_2, but_5)
        text = 'Recipients:\n'
        for i in range(len(projects_info[project_id][
                               'recipients'])):
            text += f"{i + 1}) {projects_info[project_id]['recipients'][i]}\n"
        await bot.send_message(
            message.chat.id,
            text=text,
            reply_markup=key,
        )
        messages_to_delete.append(message.message_id)
        for message_to_delete in messages_to_delete:
            await bot.delete_message(message.chat.id, message_to_delete)
        messages_to_delete.clear()

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.ADD_OWNERS
        )
    )
    async def set_project_main_message(message):
        owners.extend(message.text.split())
        person_states[message.from_user.id] = None
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addOwners')
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeOwners')
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='to_main_owner_page')
        key.add(but_1, but_2, but_5)
        text = 'Owners:\n'
        for i in range(len(owners)):
            text += f'{i + 1}) {owners[i]}\n'
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=key,
        )
        messages_to_delete.append(message.message_id)
        for message_to_delete in messages_to_delete:
            await bot.delete_message(message.chat.id, message_to_delete)
        messages_to_delete.clear()
        read_service.set_owners(owners)

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.REMOVE_OWNERS
        )
    )
    async def set_project_main_message(message):
        if not owners[int(message.text) - 1] == message.from_user.username:
            owners.pop(int(message.text) - 1)
        person_states[message.from_user.id] = None
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addOwners')
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeOwners')
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='to_main_owner_page')
        key.add(but_1, but_2, but_5)
        text = 'Owners:\n'
        for i in range(len(owners)):
            text += f'{i + 1}) {owners[i]}\n'
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=key,
        )
        messages_to_delete.append(message.message_id)
        for message_to_delete in messages_to_delete:
            await bot.delete_message(message.chat.id, message_to_delete)
        messages_to_delete.clear()
        read_service.set_owners(owners)

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.REMOVE_RECIPIENTS
        )
    )
    async def set_project_main_message(message):
        project_id = int(last_project_info[message.from_user.id]['id'])
        recip = projects_info[project_id][
            'recipients'].pop(int(message.text) - 1)
        available_project_for_customer[recip].remove(project_id)
        person_states[message.from_user.id] = None
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addRecip_' +
                                                         str(project_id))
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeRec_' +
                                                         str(project_id))
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='projectId_' +
                                                         str(project_id))
        key.add(but_1, but_2, but_5)
        text = 'Recipients:\n'
        for i in range(len(projects_info[project_id][
                               'recipients'])):
            text += f"{i + 1}) {projects_info[project_id]['recipients'][i]}\n"
        await bot.send_message(
            message.chat.id,
            text=text,
            reply_markup=key,
        )
        messages_to_delete.append(message.message_id)
        for message_to_delete in messages_to_delete:
            await bot.delete_message(message.chat.id, message_to_delete)
        messages_to_delete.clear()

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.ADD_RESPONSIBLE
        )
    )
    async def set_project_main_message(message):
        project_id = int(last_project_info[message.from_user.id]['id'])
        projects_info[project_id][
            'responsible'].extend(message.text.split())
        for resp in message.text.split():
            available_project_for_customer[resp].add(project_id)
        person_states[message.from_user.id] = None
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addResp_' +
                                                         str(project_id))
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeResp_' +
                                                         str(project_id))
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='projectId_' +
                                                         str(project_id))
        key.add(but_1, but_2, but_5)
        text = 'Responsible:\n'
        for i in range(len(projects_info[project_id][
                               'responsible'])):
            text += f"{i + 1}) {projects_info[project_id]['responsible'][i]}\n"
        await bot.send_message(
            message.chat.id,
            text=text,
            reply_markup=key,
        )
        messages_to_delete.append(message.message_id)
        for message_to_delete in messages_to_delete:
            await bot.delete_message(message.chat.id, message_to_delete)
        messages_to_delete.clear()

    @dispatcher.message_handler(
        lambda message: (
                person_states[message.from_user.id] ==
                state_machine.ProjectStates.REMOVE_RESPONSIBLE
        )
    )
    async def set_project_main_message(message):
        project_id = int(last_project_info[message.from_user.id]['id'])
        if not projects_info[project_id]['responsible'][
                   int(message.text) - 1] == message.from_user.username:
            resp = projects_info[project_id][
                'responsible'].pop(int(message.text) - 1)
            available_project_for_owner[resp].remove(project_id)
        person_states[message.from_user.id] = None
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addResp_' +
                                                         str(project_id))
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeResp_' +
                                                         str(project_id))
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='projectId_' +
                                                         str(project_id))
        key.add(but_1, but_2, but_5)
        text = 'Responsible:\n'
        for i in range(len(projects_info[project_id][
                               'responsible'])):
            text += f"{i + 1}) {projects_info[project_id]['responsible'][i]}\n"
        await bot.send_message(
            message.chat.id,
            text=text,
            reply_markup=key,
        )
        messages_to_delete.append(message.message_id)
        for message_to_delete in messages_to_delete:
            await bot.delete_message(message.chat.id, message_to_delete)
        messages_to_delete.clear()

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'projectId')
    async def get_project_options(call):
        username = call['from'].username
        if available_project_for_owner.get(username):
            await owner_funcs.get_project_options(bot, call, projects_info)
            last_project_info[call['from'].id] = {
                'id': call.data.split('_')[-1]}
        else:
            pass

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'recipients')
    async def get_project_recipients(call):
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addRecip_' +
                                                         call.data.split('_')[
                                                             -1])
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeRec_' +
                                                         call.data.split('_')[
                                                             -1])
        but_5 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='projectId_' +
                                                         call.data.split('_')[
                                                             -1])
        key.add(but_1, but_2, but_5)
        text = 'Recipients:\n'
        for i in range(len(projects_info[int(call.data.split('_')[-1])][
                               'recipients'])):
            text += f"{i + 1}) {projects_info[int(call.data.split('_')[-1])]['recipients'][i]}\n"
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=key,
        )

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'addRecip')
    async def get_project_recipients(call):
        person_states[call['from'].id] = \
            state_machine.ProjectStates.ADD_RECIPIENTS
        send_message = await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Enter extra recipients for this project separated by a space',
        )
        messages_to_delete.append(send_message.message_id)

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'addResp')
    async def get_project_recipients(call):
        person_states[call['from'].id] = \
            state_machine.ProjectStates.ADD_RESPONSIBLE
        send_message = await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Enter extra responsible for this project separated by a space'
        )
        messages_to_delete.append(send_message.message_id)

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'removeRec')
    async def get_project_recipients(call):
        person_states[call['from'].id] = \
            state_machine.ProjectStates.REMOVE_RECIPIENTS
        send_message = await bot.send_message(
            chat_id=call.message.chat.id,
            text='Enter index of recipient to delete:',
        )
        messages_to_delete.extend(
            [send_message.message_id, call.message.message_id])

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'removeResp')
    async def get_project_recipients(call):
        person_states[call['from'].id] = \
            state_machine.ProjectStates.REMOVE_RESPONSIBLE
        send_message = await bot.send_message(
            chat_id=call.message.chat.id,
            text='Enter index of responsible to delete:'
        )
        messages_to_delete.extend(
            [send_message.message_id, call.message.message_id])

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'responsible')
    async def get_project_responsible(call):
        key = types.InlineKeyboardMarkup()
        but_1 = types.InlineKeyboardButton(text='Add ➕',
                                           callback_data='addResp_' +
                                                         call.data.split('_')[
                                                             -1])
        but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                           callback_data='removeResp_' +
                                                         call.data.split('_')[
                                                             -1])
        but_3 = types.InlineKeyboardButton(text='🔙',
                                           callback_data='projectId_' +
                                                         call.data.split('_')[
                                                             -1])
        key.add(but_1, but_2, but_3)
        text = 'Responsible:\n'
        for i in range(len(projects_info[int(call.data.split('_')[-1])][
                               'responsible'])):
            text += f"{i + 1}) {projects_info[int(call.data.split('_')[-1])]['responsible'][i]}\n"
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=key,
        )

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'getMessagesNum')
    async def get_messages_num(call):
        project_id = int(call.data.split('_')[1])
        for message_to_delete in messages_to_delete:
            await bot.delete_message(call.message.chat.id, message_to_delete)
        messages_to_delete.clear()
        await owner_funcs.get_messages_num(bot, call,
                                           projects_info[int(project_id)],
                                           messages_to_delete,
                                           message_map)

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'markImportant')
    async def get_messages_num(call):
        project_id = int(call.data.split('_')[1])
        m_id = int(call.data.split('_')[2])
        message = \
            [m for m in projects_info[project_id]['messages'] if
             m['message_id'] == m_id][0]
        message['importance_marker'] = not message['importance_marker']
        myquery = {"message_id": message['message_id']}
        newvalues = {
            "$set": {"importance_marker": message['importance_marker']}}
        data_base.current_DB[projects_info[project_id]['name']].update_one(
            myquery, newvalues)
        await owner_funcs.mark_important(bot, call, project_id, message)

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'del')
    async def delete_project(call):
        project_id = int(call.data.split('_')[1])
        project_name = projects_info[project_id]['name']
        data_base.current_DB[project_name].delete_many({})
        projects_info.pop(project_id)
        username = call['from'].username
        await owner_funcs.show_available_projects(
            bot,
            call,
            available_project_for_owner[username],
            projects_info,
        )

    @dispatcher.callback_query_handler(
        lambda call: call.data.split('_')[0] == 'deleteMessage')
    async def delete_message(call):
        project_id = int(call.data.split('_')[1])
        m_id = int(call.data.split('_')[2])
        message = \
            [m for m in projects_info[project_id]['messages'] if
             m['message_id'] == m_id][0]
        message['archived'] = not message['archived']
        myquery = {"message_id": message['message_id']}
        newvalues = {"$set": {"archived": message['archived']}}
        data_base.current_DB[projects_info[project_id]['name']].update_one(
            myquery, newvalues)
        messages_to_delete.remove(call.message.message_id)
        await bot.delete_message(call.message.chat.id, call.message.message_id)

    @dispatcher.callback_query_handler(lambda call: True)
    async def callback_inline(call):
        if call.data == 'shutdown':
            # TODO: save everything into db
            await bot.send_message(
                chat_id=call.message.chat.id,
                text='All data saved, bye!'
            )
            await bot.delete_message(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id)
            sys.exit(0)
        elif call.data == 'new_project':
            last_project_info[call.message.chat.id][
                'start_message'] = call.message
            await owner_funcs.create_project(
                bot, call.message.chat.id, person_states, messages_to_delete
            )
        elif call.data == 'to_main_owner_page':
            await owner_funcs.main_page(bot, call)
        elif call.data == 'add_owners':
            await owner_funcs.get_owners(bot, call, owners)
        elif call.data == 'addOwners':
            await owner_funcs.add_owner(bot, call, person_states,
                                        messages_to_delete)
        elif call.data == 'removeOwners':
            await owner_funcs.remove_owner(bot, call, person_states,
                                           messages_to_delete)
        elif call.data.split('_')[0] == 'CustProjectId':
            await customer_funcs.get_messages_for_project(
                bot, call, projects_info, int(call.data.split('_')[-1]),
                person_states)
        elif call.data == 'to_main_customer_page':
            await customer_funcs.main_customer_page(
                bot, call,
                available_project_for_customer[call.message['from'].username],
                projects_info)
            person_states[call.message.from_user.id] = None
        elif call.data.split('_')[0] == 'rubbish':
            await owner_funcs.get_all_archived(bot, call, projects_info)
        elif call.data.split('_')[0] == 'clear':
            myquery = {"archived": True}
            data_base.current_DB[projects_info[int(call.data.split('_')[-1])][
                'name']].delete_many(myquery)
            await owner_funcs.get_all_archived(bot, call, projects_info)
        elif call.data == 'to_main_manager_page':
            await owner_funcs.main_manager_page(bot, call)
        elif call.data.split('_')[0] == 'ManagerProjectId':
            await owner_funcs.manager_show_propert_proj(bot, call,
                                                        projects_info)
        elif call.data == 'available_projects':
            username = call['from'].username
            if available_project_for_owner.get(username) and username in owners:
                await owner_funcs.show_available_projects(
                    bot,
                    call,
                    available_project_for_owner[username],
                    projects_info,
                )
            elif available_project_for_owner.get(
                    username) and username not in owners:
                await owner_funcs.show_available_projects_manager(
                    bot,
                    call,
                    available_project_for_owner[username],
                    projects_info,
                )
            elif available_project_for_customer.get(username):
                await customer_funcs.main_customer_page(
                    bot, call,
                    available_project_for_customer[username],
                    projects_info)
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
        if message.reply_to_message:
            original_message = message_map[message.reply_to_message.message_id]
            await bot.send_message(
                original_message['chat_id'],
                text=message.text,
                reply_to_message_id=original_message['message_id']
            )
        elif person_states[message['from'].id]:
            if person_states[message['from'].id].split('_')[
                0] == 'WRITEPROJECTMESSAGES':
                data_base.insert_into_db(projects_info[int(
                    person_states[message.from_user.id].split('_')[-1])][
                                             'name'], message, False, 'text')
                await bot.send_message(message.from_user.id, 'Message received')
        logger.info('Get text message %s', message)
        # TODO: if it is currently in the project,
        #  throw his message into the database

    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
