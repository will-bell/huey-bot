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


def generate_excuse() -> str:
    return choice(negatives) + ' ' + choice(reasons) + ' ' + choice(extra)
