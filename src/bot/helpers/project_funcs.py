import typing


def save_project_info(
        last_project_info,
        available_project_for_customer: typing.DefaultDict[
            typing.AnyStr, typing.Set],
        available_project_for_owner: typing.DefaultDict[
            typing.AnyStr, typing.Set],
        projects_info: typing.DefaultDict[typing.AnyStr, typing.Dict],
):
    for username in last_project_info['responsible'].split():
        username = username.strip().replace('@', '')
        available_project_for_owner[username].add(last_project_info['id'])
    for username in last_project_info['recipients'].split():
        username = username.strip().replace('@', '')
        available_project_for_customer[username].add(last_project_info['id'])
    projects_info[last_project_info['id']] = {
        'name': last_project_info['name'],
        'main_message': last_project_info['main_message'],
        'recipients': last_project_info['recipients'].split(),
        'responsible': last_project_info['responsible'].split(),
    }
    print('save', projects_info)
    # TODO: save to db
