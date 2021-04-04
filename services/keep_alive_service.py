import time
from multiprocessing import Value

import requests
from common import send_message

# from services.post_service import post_queue


def keep_alive(loop: bool):
    url = 'https://huey-bot.herokuapp.com/keep_alive'
    
    last_time = time.time()
    while loop:
        if time.time() - last_time > 10:
            # post_queue(send_message, 'ping')
            
            send_message('ping')
            
            requests.post(url=url)
            
            last_time = time.time()


if __name__ == '__main__':
    keep_alive(True)
