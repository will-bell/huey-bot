import time
from multiprocessing import Value

import requests

from common import send_message
from post_service import post_queue


def keep_alive(loop: Value):
    url = 'https://huey-bot.herokuapp.com/keep_alive'
    
    last_time = time.time()
    while loop.value:
        if time.time() - last_time > 1:
            res = requests.post(url=url)

            if res.status_code == 200:
                post_queue.enqueue(send_message, "Ping")

            last_time = time.time()
