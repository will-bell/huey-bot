import time

import requests


def keep_alive_service(loop: bool):
    url = 'https://huey-bot.herokuapp.com/keep_alive'
    
    last_time = time.time()
    while loop:
        if time.time() - last_time > 20:
            requests.post(url=url)
            last_time = time.time()
