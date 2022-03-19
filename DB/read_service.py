import yaml


def get_mongo_url():
    with open('service.yaml', encoding='utf-8') as file:
        parameters = yaml.safe_load(file)
        return parameters.get('url')

if __name__ == '__main__':
    print(get_url())
