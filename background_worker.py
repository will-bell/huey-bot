from multiprocessing import Process
import time

from services.keep_alive_service import keep_alive_service
from services.steam_services import online_status_service


if __name__ == '__main__':
    keep_alive_process = Process(target=keep_alive_service, args=(True,))
    online_status_process = Process(target=online_status_service, args=(True,))

    keep_alive_process.start()
    online_status_process.start()

    while True:
        time.sleep(1)