import logging
import time

from flask import Flask, request

from common import send_message
from interaction.conversation import (generate_excuse, no_prompt, oi_huey,
                                      question_about_friends_online,
                                      question_about_last_game,
                                      request_to_do_something)
from services.dota_game_service import (generate_old_game_notification,
                                        get_last_match_data)
from services.steam_service import generate_friends_online_message

app = Flask(__name__)

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route('/', methods=['POST'])
def webhook():
    app.logger.debug('Got a message!')

    # Comfortable amount of time to not cause a graphical glitch in GroupMe
    time.sleep(1)

    data = request.get_json()

    if data['name'] != 'Huey':
        if oi_huey(data):
            if question_about_last_game(data):
                send_message(generate_old_game_notification(get_last_match_data()))

            elif question_about_friends_online(data):
                send_message(generate_friends_online_message())

            elif request_to_do_something(data):
                send_message(generate_excuse())

            else:
                send_message(no_prompt())
        
    return "ok", 200


@app.route('/keep_alive', methods=['POST'])
def keep_alive_webhook():
    app.logger.debug('Keep alive route received a ping')
    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
