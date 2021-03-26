import os
from random import choice
from time import sleep
from typing import List

import requests
from flask import Flask, request

app = Flask(__name__)

names = [
    'houston',
    'huey',
    '@houston',
    '@houston holsenback',
    '@huey'
]

greetings = [
    'oi',
    'where you at',
    'where are you',
    'play dota',
    'play some dota',
    'play war thunder',
    'play some war thunder',
    'dota?',
    'war thunder?', 
    'get on'
]

negatives = [
    "Be on in 40 I gotta",
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
    "eat dinner in two hours",
    "go buy Gatorade for my dad",
    "go buy soy sauce", 
    "go get my mom's purse she left at the gas station",
    "mow a rich guy's field",
    "drive this tractor down a country mile",
    "kick a can down a country mile",
    "beat Waco 'til he shuts up",
    "ignore Grady for a bit"
]

extra = [
    "shouldn't take too long",
    "be on after that",
    "don't worry about it"
]

extra = extra + [' ' for _ in range(len(extra))]

def detect(text: str, options: List[str]) -> bool:
    for option in options:
        if option in text:
            return True

    return False

def oi_huey(data) -> bool:
    lower_text = data['text'].lower()
    if detect(lower_text, names):
        if detect(lower_text, greetings):
            return True

    return False

@app.route('/', methods=['POST'])
def webhook():
    sleep(1)

    data = request.get_json()

    # We don't want to reply to ourselves!
    if data['name'] != 'Huey':
        if oi_huey(data):
            message = choice(negatives) + ' ' + choice(reasons) + ' ' + choice(extra)

            send_message(message)

    return "ok", 200


def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text'   : msg,
            }

    res = requests.post(url, json=data, headers={})
