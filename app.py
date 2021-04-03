import logging
import time
from multiprocessing import Manager, Process, Value

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from common import send_message, send_message_tony
from interaction.conversation import (generate_excuse, no_prompt, oi_huey,
                                      question_about_friends_online,
                                      question_about_last_game,
                                      request_to_do_something, tony_response)
from services.dota_game_service import (dota_game_service,
                                        generate_old_game_notification,
                                        get_last_match_data)
from services.keep_alive_service import keep_alive
from services.steam_service import generate_friends_online_message

app = Flask(__name__)

if __name__ == '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# db_name = 'last_game_state.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# class RecentGamesDB(db.Model):
#     match_id = db.Column(db.Integer, primary_key=True)
#     start_time = db.Column(db.Integer)
#     side = db.Column(db.String(7))
#     victory = db.Column(db.Integer)
#     duration = db.Column(db.Integer)
#     hero = db.Column(db.String(30))
#     kills = db.Column(db.Integer)
#     deaths = db.Column(db.Integer)
#     assists = db.Column(db.Integer)
#     with_heroes = db.Column(db.String(150))
#     with_friends = db.Column(db.String(30))
#     against_heroes = db.Column(db.String(150))

#     def __repr__(self):
        # return f'Match {self.match_id}'


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
                send_message_tony(tony_response())

                
            elif question_about_friends_online(data):
                send_message(generate_friends_online_message())
                send_message_tony(tony_response())
            elif request_to_do_something(data):
                send_message(generate_excuse())
                send_message_tony(tony_response())

            else:
                send_message(no_prompt())

        
    return "ok", 200


@app.route('/keep_alive', methods=['POST'])
def keep_alive_webhook():
    app.logger.debug('Keep alive route received a ping')
    return "ok", 200


if __name__ == '__main__':
    manager = Manager()
    last_game_state = manager.Namespace()
    last_game_state.last_query_time = time.time()
    last_game_state.match_id = -1
    last_game_state.start_time = -1
    last_game_state.side = ''
    last_game_state.victory = 0
    last_game_state.duration = -1
    last_game_state.hero = ''
    last_game_state.kills = -1
    last_game_state.deaths = -1
    last_game_state.assists = -1
    last_game_state.with_heroes = tuple()
    last_game_state.with_friends = tuple()
    last_game_state.against_heroes = tuple()
    last_game_state.houstons_GPM = -1
    last_game_state.friends_deaths = {}

    p = Process(target=dota_game_service, args=(last_game_state,))
    p.start()

    value = Value('b', True)
    p2 = Process(target=keep_alive, args=(value,))
    p2.start()

    app.run(debug=True, use_reloader=False)
    
    p.join()
    p2.join()
