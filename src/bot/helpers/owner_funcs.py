from aiogram import types
from DB.DB_management import DBManagement
from bot.helpers import state_machine


def get_main_key():
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Available projects",
                                       callback_data="available_projects")
    but_2 = types.InlineKeyboardButton(text="New project",
                                       callback_data="new_project")
    but_3 = types.InlineKeyboardButton(text="Owners",
                                       callback_data="add_owners")
    but_4 = types.InlineKeyboardButton(text="Shutdown 🚫",
                                       callback_data="shutdown")
    key.add(but_1, but_2, but_3, but_4)
    return key


async def start_func(bot, message):
    key = get_main_key()
    name = message['from']['first_name'] or message['from']['username']
    await bot.send_message(
        message.chat.id, f'Hi, {name}! Select one:', reply_markup=key,
    )


async def main_page(bot, call):
    key = get_main_key()
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='Select one:',
        reply_markup=key,
    )


async def create_project(bot, person_id, person_states, messages_to_delete):
    person_states[person_id] = state_machine.ProjectStates.PROJECT_NAME
    send_message = await bot.send_message(person_id, 'Enter the project name:')
    messages_to_delete.append(send_message.message_id)


async def do_work_after_collecting_data(
        bot, project_info, messages_to_delete, chat_id,
):
    for message_to_delete in messages_to_delete:
        await bot.delete_message(chat_id, message_to_delete)
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='to_main_owner_page')
    key.add(but_1)
    await bot.edit_message_text(
        chat_id=project_info['start_message'].chat.id,
        message_id=project_info['start_message'].message_id,
        text=f'All project data collected:\n'
             f'Name: {project_info["name"]}\n'
             f'Description: {project_info["description"]}\n'
             f'Responsible: {project_info["responsible"]}\n'
             f'Main message: {project_info["main_message"]}\n'
             f'Recipients: {project_info["recipients"]}\n\n'
             f'Share this link with recipients: '
             f'https://t.me/mango_humans_assistant_bot',
        reply_markup=key,
    )
    data_base = DBManagement()
    del project_info['start_message']
    data_base.insert_information_about_projects(
        project_info['name'],
        project_info,
    )


async def show_available_projects(bot, call, available_projects, projects_info):
    key = types.InlineKeyboardMarkup(row_width=2)
    buts = []
    for available_project in available_projects:
        if projects_info[available_project]:
            buts.append(
                types.InlineKeyboardButton(
                    text=projects_info[available_project]['name'],
                    callback_data='projectId_' + str(available_project),
                )
            )
    but_1 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='to_main_owner_page')
    key.add(*buts, but_1)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='Choose one of projects:',
        reply_markup=key,
    )


async def get_project_options(bot, call, projects_info):
    key = types.InlineKeyboardMarkup()
    project_id = call.data.split('_')[-1]
    but_1 = types.InlineKeyboardButton(text='Get messages',
                                       callback_data='getMessages_' + project_id)
    but_2 = types.InlineKeyboardButton(text='Recipients',
                                       callback_data='recipients_' + project_id)
    but_3 = types.InlineKeyboardButton(text='Responsible',
                                       callback_data='responsible_' + project_id)
    but_4 = types.InlineKeyboardButton(text='Delete ❌',
                                       callback_data='del_' + project_id)
    but_5 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='available_projects')
    key.add(but_1, but_2, but_3, but_4, but_5)
    print(projects_info)
    print(project_id)
    text = 'Project description:\n' + projects_info[int(project_id)][
        'description'] + '\n\n'
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text + 'Choose one of options:',
        reply_markup=key,
    )


async def get_messages(bot, call):
    key = types.InlineKeyboardMarkup()
    project_id = call.data.split('_')[-1]
    but_1 = types.InlineKeyboardButton(text='Get 10 messages',
                                       callback_data='getMessagesNum_' + project_id + '_10_0')
    but_2 = types.InlineKeyboardButton(text='Get 50 messages',
                                       callback_data='getMessagesNum_' + project_id + '_50_0')
    but_3 = types.InlineKeyboardButton(text='Get all messages',
                                       callback_data='getMessagesNum_' + project_id + '_-1_0')
    but_4 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='projectId_' + project_id)

    key.add(but_1, but_2, but_3)
    key.add(but_4)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='View messages:',
        reply_markup=key,
    )


def generate_message_key(project_id, m):
    message_key = types.InlineKeyboardMarkup()
    btn1_text = 'Mark as unimportant' if m[
        'important'] else '✅ Mark as important'
    m_id = m['id']
    mbut_1 = types.InlineKeyboardButton(text=btn1_text,
                                        callback_data=f'markImportant_{project_id}_{m_id}')
    mbut_2 = types.InlineKeyboardButton(text='❌ Delete',
                                        callback_data=f'deleteMessage_{project_id}_{m_id}')
    message_key.add(mbut_1, mbut_2)
    return message_key


async def get_messages_num(bot, call, project, messages_to_delete):
    project_id = call.data.split('_')[1]
    num = int(call.data.split('_')[2])
    page = int(call.data.split('_')[3])

    print(project)

    messages = [m for m in project['messages'] if not m['deleted']][
               page * num:(page + 1) * num]
    if num == -1:
        messages = project['messages']

    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='<',
                                       callback_data=f'getMessagesNum_{project_id}_{num}_{page - 1}')
    but_2 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='getMessages_' + project_id)
    but_3 = types.InlineKeyboardButton(text='>',
                                       callback_data=f'getMessagesNum_{project_id}_{num}_{page + 1}')

    if page > 0:
        if (page + 1) * num < len(project['messages']):
            key.add(but_1, but_2, but_3)
        else:
            key.add(but_1, but_2)
    else:
        if (page + 1) * num < len(project['messages']) and num != -1:
            key.add(but_2, but_3)
        else:
            key.add(but_2)

    for m in messages:
        message = await bot.send_message(call.message.chat.id, text=m['text'],
                                         reply_markup=generate_message_key(
                                             project_id, m))
        messages_to_delete.append(message.message_id)

    message = await bot.send_message(call.message.chat.id, text='Navigation',
                                     reply_markup=key)

    messages_to_delete.append(message.message_id)


async def mark_important(bot, call, project_id, m):
    text = ''
    if m['important']:
        text = '✅' + call.message.text
    else:
        text = call.message.text[1:]
    m['text'] = text
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=generate_message_key(project_id, m),
    )


async def get_owners(bot, call, owners):
    text = 'Owners:\n'
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='Add ➕',
                                       callback_data='addOwners')
    but_2 = types.InlineKeyboardButton(text='Remove ➖',
                                       callback_data='removeOwners')
    but_3 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='to_main_owner_page')
    key.add(but_1, but_2, but_3)
    for i in range(len(owners)):
        text += f'{i + 1}) {owners[i]}\n'
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=key,
    )


async def remove_owner(bot, call, person_states, messages_to_delete):
    send_mess = await bot.send_message(
        chat_id=call.message.chat.id,
        text='Enter index owner to remove:'
    )
    person_states[call['from'].id] = state_machine.ProjectStates.REMOVE_OWNERS
    messages_to_delete.extend([send_mess.message_id, call.message.message_id])


async def add_owner(bot, call, person_states, messages_to_delete):
    send_mess = await bot.send_message(
        chat_id=call.message.chat.id,
        text='Add extra owner username:'
    )
    person_states[call['from'].id] = state_machine.ProjectStates.ADD_OWNERS
    messages_to_delete.extend([send_mess.message_id, call.message.message_id])
