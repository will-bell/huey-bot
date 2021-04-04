import os

import requests

GROUPME_API_URL = 'https://api.groupme.com/v3/bots/post'


def send_message_as_huey(message: str):
    data = {
            'bot_id': os.getenv('GROUPME_BOT_ID'),
            'text':   message,
            }

    requests.post(url=GROUPME_API_URL, json=data)


def send_message_as_tony(message: str):
    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID_TONY'),
        'text':   message,
    }
    requests.post(url=GROUPME_API_URL, json=data)


def send_message_to_test_group(message: str):
    data = {
        'bot_id': os.getenv('GROUPME_TESTBOT_ID'),
        'text':   message,
    }
    requests.post(url=GROUPME_API_URL, json=data)
