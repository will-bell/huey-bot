from random import choice, random
from typing import List

from .text_phrases import (EXTRA, GREETINGS, NAMES, NEGATIVES, REASONS,
                           REQUESTS, WHAT, TONY_NICKNAMES, TONY_PHRASES)


def detect(text: str, options: List[str]) -> bool:
    for option in options:
        if option in text:
            return True

    return False


def oi_huey(data) -> bool:
    lower_text = data['text'].lower()
    if detect(lower_text, NAMES):
        if detect(lower_text, GREETINGS) or detect(lower_text, '@'):
            return True

    return False


def request_to_do_something(data: dict) -> bool:
    lower_text = data['text'].lower()
    
    if detect(lower_text, REQUESTS):
        return True

    return False


def generate_excuse() -> str:
    return choice(NEGATIVES) + ' ' + choice(REASONS) + ' ' + choice(EXTRA)


def sum_markers(text: str, markers: List[str]) -> int:
    marker_sum = 0
    for marker in markers:
        if marker in text:
            marker_sum += 1

    return marker_sum


LAST_GAME_MARKERS = ["how", "how'd", 'that', 'last', 'game', 'was', 'it', 'go']


def question_about_last_game(data: dict) -> bool:
    lower_text = data['text'].lower()

    marker_sum = sum_markers(lower_text, LAST_GAME_MARKERS)
    
    return marker_sum > 3


FRIENDS_ONLINE_MARKERS = ["who's", "who is", "is anyone", "online", "playing", "on"]


def question_about_friends_online(data: dict) -> bool:
    lower_text = data['text'].lower()

    return sum_markers(lower_text, FRIENDS_ONLINE_MARKERS) > 1


def no_prompt():
    return choice(WHAT)

def tony_response():
    if random() <= 0.5:
        return choice(TONY_PHRASES) + ' ' + choice(TONY_NICKNAMES)
    else:
        return None
