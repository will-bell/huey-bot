from random import choice
from typing import List

from .text_phrases import extra, greetings, names, negatives, reasons


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


LAST_GAME_MARKERS = ["how", "how'd", 'that', 'last', 'game', 'was', 'it', 'go']


def question_about_last_game(data) -> bool:
    lower_text = data['text'].lower()

    marker_sum = 0
    for marker in LAST_GAME_MARKERS:
        if marker in lower_text:
            marker_sum += 1
    
    return marker_sum > 3


def generate_excuse() -> str:
    return choice(negatives) + ' ' + choice(reasons) + ' ' + choice(extra)
