import json
import os
import subprocess
import urllib.request

import speech_recognition as sr

from bot.helpers import read_yaml


async def oga2wav(file_name):
    src_filename = file_name
    dest_filename = file_name + '.wav'
    subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
    return await wav2text(dest_filename, file_name)


async def wav2text(dest_filename, file_name):
    recognizer = sr.Recognizer()
    message = sr.AudioFile(dest_filename)

    with message as source:
        audio = recognizer.record(source)
    try:
        result = recognizer.recognize_google(audio, language='ru_RU')
        os.remove(dest_filename)
        os.remove(file_name)
        return format(result)

    except sr.UnknownValueError:
        os.remove(dest_filename)
        os.remove(file_name)
        return 'Не удалось распознать текст'


async def download(file_path, file_id):
    url = (
        f'https://api.telegram.org/file/bot{read_yaml.get_token_tg()}/'
        + file_path
    )
    urllib.request.urlretrieve(url, file_id + '.oga')
    file_name = file_id + '.oga'
    return await oga2wav(file_name)


async def request2text(file_id, session):
    request = session.get(
        'https://api.telegram.org/bot'
        + read_yaml.get_token_tg()
        + f'/getFile?file_id={file_id}'
    )
    content = json.loads(request.text)

    return await download(
        content['result']['file_path'], content['result']['file_id']
    )
