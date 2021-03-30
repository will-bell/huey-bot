import time
from multiprocessing import Value

import requests

from common import send_message

def keep_alive(loop: Value):
    url = 'https://huey-bot.herokuapp.com/keep_alive'
    
    last_time = time.time()
    while loop.value:
        if time.time() - last_time > 10:
            res = requests.post(url=url)
            # print('ping')
            last_time = time.time()

            send_message("I'm still alive")
