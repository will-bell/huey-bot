from multiprocessing import Value
import time
import requests


def keep_alive(loop: Value):
    url = 'https://huey-bot.herokuapp.com/keep_alive'
    
    last_time = time.time()
    while loop.value:
        if time.time() - last_time > 60:
            res = requests.post(url=url)
            # print('ping')
            last_time = time.time()
