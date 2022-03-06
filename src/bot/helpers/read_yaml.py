import yaml


def get_token_tg():
    with open("src/settings.yaml") as file:
        parameters = yaml.safe_load(file)
        return parameters.get("telegram_api_token")
