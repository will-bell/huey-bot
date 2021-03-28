import os
from multiprocessing import Process, Value
from time import sleep

import requests
from flask import Flask, request

from interaction.conversation import generate_excuse, oi_huey
from services.dota_game_service import dota_game_service


app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    # Comfortable amount of time to not cause a graphical glitch in GroupMe
    sleep(1)

    data = request.get_json()

    if data['name'] != 'Huey':
        if oi_huey(data):
            send_message(generate_excuse())

    return "ok", 200


def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text'   : msg,
            }

    res = requests.post(url, json=data, headers={})


class Loops():

    def __init__():
        loop = Value('b', True)

        self._game_check = Process(target=)


if __name__ == '__main__':
    recording_on = Value('b', True)
    p = Process(target=check_loop, args=(recording_on,))
    p.start()  
    app.run(debug=False, use_reloader=False)
    p.join()
