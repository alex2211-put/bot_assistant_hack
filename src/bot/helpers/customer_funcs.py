from aiogram import types

from bot.helpers import state_machine


def get_main_key():
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Available projects",
                                       callback_data="available_projects")
    but_2 = types.InlineKeyboardButton(text="New project",
                                       callback_data="new_project")
    but_3 = types.InlineKeyboardButton(text="Shutdown",
                                       callback_data="shutdown")
    key.add(but_1, but_2, but_3)
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


async def show_available_projects(bot, call, available_projects, projects_info):
    key = types.InlineKeyboardMarkup(row_width=2)
    buts = []
    for available_project in available_projects:
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


async def get_project_options(bot, call):
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='Get messages',
                                       callback_data='allMess_' +
                                                     call.data.split('_')[-1])
    but_2 = types.InlineKeyboardButton(text='Recipients',
                                       callback_data='recipients_' +
                                                     call.data.split('_')[-1])
    but_3 = types.InlineKeyboardButton(text='Responsible',
                                       callback_data='responsible_' +
                                                     call.data.split('_')[-1])
    but_4 = types.InlineKeyboardButton(text='Delete ❌',
                                       callback_data='del_' +
                                                     call.data.split('_')[-1])
    but_5 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='available_projects')
    key.add(but_1, but_2, but_3, but_4, but_5)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text='Choose one of options:',
        reply_markup=key,
    )
