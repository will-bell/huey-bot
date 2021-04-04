import os

import requests



def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text'   : msg,
            }

    res = requests.post(url, json=data, headers={})


def send_message_tony(msg):
    if msg is not None:
        url = 'https://api.groupme.com/v3/bots/post'

        data = {
            'bot_id': os.getenv('GROUPME_BOT_ID_TONY'),
            'text': msg,
        }
        res = requests.post(url, json=data, headers={})
