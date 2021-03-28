import time
from multiprocessing import Manager, Process

from flask import Flask, request

from common import send_message
from interaction.conversation import generate_excuse, oi_huey, question_about_last_game
from services.dota_game_service import dota_game_service, generate_old_game_notification

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    # Comfortable amount of time to not cause a graphical glitch in GroupMe
    time.sleep(1)

    data = request.get_json()

    if data['name'] != 'Huey':
        if oi_huey(data):
            send_message(generate_excuse())

        elif question_about_last_game(data):
            send_message(generate_old_game_notification(last_game_state))

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

    p = Process(target=dota_game_service, args=(last_game_state,))
    p.start()  
    app.run(debug=False, use_reloader=False)
    p.join()
