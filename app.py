import os
from random import choice
from time import sleep

import requests
from flask import Flask, request

app = Flask(__name__)

prefixes = [
    "Play without me I have to",
    "Sorry guys I can't I gotta",
    "Maybe later first I have to",
    "Hold up I just gotta"
]

reasons = [
    "do my dad's taxes",
    "move scrap metal",
    "drive my sister to her friend's house",
    "pick up my sister from a party",
    "watch paint dry",
    "take my mom to the store",
    "hold the light for my dad",
    "do every dog related chore",
    "go to Grenada for the third time today",
    "eat in dinner in two hours",
    "go buy Gatorade for my dad",
    "go buy soy sauce"
]


def oi_huey(data):
    if '@Huey' in data['text']:
        if 'oi' in data['text'].lower():
            return True

    return False

@app.route('/', methods=['POST'])
def webhook():
    sleep(2)

    data = request.get_json()

    # We don't want to reply to ourselves!
    if data['name'] != 'Huey':
        if oi_huey(data):
            message = choice(prefixes) + ' ' + choice(reasons)

    send_message(message)

    return "ok", 200


def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text'   : msg,
            }
            
    res = requests.post(url, json=data, headers={})
