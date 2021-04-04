import os

import requests
from rq import Queue

from worker import conn

HUEY_BOT_ID = os.getenv('HUEY_BOT_ID')
TONY_BOT_ID = os.getenv('TONY_BOT_ID')

GROUPME_API_URL = 'https://api.groupme.com/v3/bots/post'


def post_message_as_huey(msg: str):
    data = {
            'bot_id':   HUEY_BOT_ID,
            'text':     msg,
            }

    requests.post(GROUPME_API_URL, json=data)


def post_message_as_tony(msg: str):
    data = {
            'bot_id':   TONY_BOT_ID,
            'text':     msg,
            }

    requests.post(GROUPME_API_URL, json=data)


post_queue = Queue('post', connection=conn)
