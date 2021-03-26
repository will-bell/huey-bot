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
    "ignore Grady for a bit",
    "watch this water evaporate",
    "clean my mom's mixing bowl",
    "hold my sister hair while she pukes",
    "watch the Florida Gators lose to LSU",
    "rewatch the Tim Tebow documentary again",
    "take my sister to get covid tested",
    "bring my mom her checkbook",
    "watch this paint dry",
    "make sure the grass is growing okay",
    "take my dogs out",
    "walk my dogs",
    "go to the store for some pie crust",
    "help my dad work on the Diesel",
    "get elbowed in the nose by Big John",
    "help my dad at te construction site",
    "farm",
    "drive to Grenada",
    "drive back from Grenada",
    "take my mom and sister to Grenada",
    "drive Waco to Texas to see Elijah",
    "drive my sister to get another dog",
    "go get some more hotdogs are Kroger",
    "grill some hamburgers",
    "eat some steak",
    "strike a Tim Tebow pose",
    "come here and do something for my mom right now",
    "click my lighter",
    "go eat with a friend",
    "make sure the carpet is still clean",
    "tap on the walls to make sure there aren't any termites",
    "recruit 5 friends to my gifting circle",
    "make some brownies",
    "try to get my power turned back on",
    "call AT&T, my internet is out",
    "make sure my dad took all his vitamins today",
    "make my bed",
    "take a shower",
    "go buy a new headset, my dad threw mine at the wall and it exploded",
    "make sure Levi still has all 4 legs",
    "go buy some more chicken stock",
    "make sure te Diesel has enoug tire pressure",
    "move some dirt",
    "count how many boards are in our fence",
    "take the trash to the curb",
    "make sure my sisters toast isn't too hot for her to eat",
    "keep an eye on the pie in the oven",
    "thaw some fish for my mom",
    "stare into the endless abyss and ponder the meaning of dread and existence",
    "clean my parents' bedroom windows",
    "make sure all the wiring on the thermostat is up to code",
    "count how many cups we have in our cabinet",
    "go plant some trees",
    "fill up my water bottle",
    "go weight the kitchen table and make sure its not too heavy",
    "call my dad and see what time he wants dinner",
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
