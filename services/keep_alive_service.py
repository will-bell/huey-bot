import time

import requests

HUEY_IS_ALIVE_URL = 'https://huey-bot.herokuapp.com/is_alive'


def keep_alive_service(loop: bool):
    last_time = time.time()
    while loop:
        if time.time() - last_time > 20:
            requests.post(url=HUEY_IS_ALIVE_URL)
            last_time = time.time()
