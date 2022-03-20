from aiogram import types


def get_main_key():
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text="Available projects",
                                       callback_data="available_projects")
    key.add(but_1)
    return key


async def start_func(bot, message, available_projects, projects_info):
    key = types.InlineKeyboardMarkup(row_width=2)
    buts = []
    for available_project in available_projects:
        if projects_info[available_project]:
            buts.append(
                types.InlineKeyboardButton(
                    text=projects_info[available_project]['name'],
                    callback_data='CustProjectId_' + str(available_project),
                )
            )
    key.add(*buts)
    if key:
        await bot.send_message(
            chat_id=message.chat.id,
            text='Choose one of projects:',
            reply_markup=key,
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text='No projects available for you.',
        )


async def main_customer_page(bot, call, available_projects, projects_info):
    key = types.InlineKeyboardMarkup(row_width=2)
    buts = []
    for available_project in available_projects:
        if projects_info[available_project]:
            buts.append(
                types.InlineKeyboardButton(
                    text=projects_info[available_project]['name'],
                    callback_data='CustProjectId_' + str(available_project),
                )
            )
    key.add(*buts)
    if key:
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Choose one of projects:',
            reply_markup=key,
        )
    else:
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='No projects available for you.',
            reply_markup=key,
        )


async def get_messages_for_project(bot, call, projects_info, project_id,
                                   person_states):
    key = types.InlineKeyboardMarkup()
    but_1 = types.InlineKeyboardButton(text='🔙',
                                       callback_data='to_main_customer_page')
    key.add(but_1)
    text = 'Description:\n' + projects_info[project_id][
        'main_message'] + '\n\n' + 'I am ready to receive you messages. ' + \
           'You can write me, I will remember them'
    person_states[call.message.chat.id] = 'WRITEPROJECTMESSAGES_' + str(
        project_id)
    print(person_states)
    await bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=key,
    )
