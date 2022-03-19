import yaml


def get_mongo_url():
    with open('service.yaml', encoding='utf-8') as file:
        parameters = yaml.safe_load(file)
        return parameters.get('url')


def get_owners():
    with open('service.yaml', encoding='utf-8') as file:
        parameters = yaml.safe_load(file)
        return parameters.get('owners')


def set_owners(owners):
    parameters = {}
    with open('service.yaml', 'r', encoding='utf-8') as file:
        parameters = yaml.safe_load(file)
    with open('service.yaml', 'w', encoding='utf-8') as file:
        parameters['owners'] = owners
        yaml.safe_dump(parameters, file)
