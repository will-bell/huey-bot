import os
import time
from multiprocessing import Manager, Process
# from sqlalchemy.sql import text
from typing import NamedTuple, Tuple

import requests
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

from common import send_message
from interaction.conversation import (generate_excuse, oi_huey,
                                      question_about_last_game)

# from services.dota_game_service import (dota_game_service,
#                                         generate_old_game_notification)

app = Flask(__name__)

# db_name = 'last_game_state.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# db = SQLAlchemy(app)


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
#         return f'Match {self.match_id}'


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


API_URL = "https://api.opendota.com/api/"

HERO_DATA_URL = API_URL + 'heroes'
hero_data_json = requests.get(url=HERO_DATA_URL).json()
HERO_MAP = {}
for entry in hero_data_json:
    HERO_MAP[entry['id']] = entry

PLAYER_ID = int(os.getenv('PLAYER_ID'))
PLAYER_MATCHES_URL = API_URL + f'players/{PLAYER_ID}/matches'
PLAYER_REFRESH_URL = API_URL + f'players/{PLAYER_ID}/refresh'

MATCHES_URL = API_URL + 'matches/'

FRIENDS_MAP = {
    120813182: 'Gavin',
    106692261: 'Blake',
    112984717: 'Grady',
    95549436: 'Kevin',
    133187493: 'Jake',
    55335864: 'Steve',
    126859835: 'Tony',
}


class LastGameState(NamedTuple):
    # For not pinging the website too often
    last_query_time: float

    # Match data
    match_id: int
    start_time: int
    side: str
    victory: bool
    duration: int
    
    # Player data
    hero: str
    kills: int
    deaths: int
    assists: int

    # Teammates
    with_heroes: Tuple[str]
    with_friends: Tuple[str]

    # Enemies
    against_heroes: Tuple[str]


def update_last_game_state(last_game_state: LastGameState, match_data: dict):
    # Fill out the match data fields
    last_game_state.match_id = match_data['match_id']
    last_game_state.start_time = match_data['start_time']

    player_data = None
    for entry in match_data['players']:
        if entry['account_id']:
            if int(entry['account_id']) == PLAYER_ID:
                player_data = entry
                break
    
    last_game_state.side = 'Radiant' if player_data['isRadiant'] else 'Dire'
    last_game_state.victory = bool(player_data['win'])
    last_game_state.duration = int(player_data['duration'] / 60)
    
    # Fill out the player data fields
    last_game_state.hero = HERO_MAP[player_data['hero_id']]['localized_name']
    last_game_state.kills = player_data['kills']
    last_game_state.deaths = player_data['deaths']
    last_game_state.assists = player_data['assists']

    # Find heroes on either side and friends
    with_heroes = []
    against_heroes = []
    with_friends = []
    player_is_radiant = player_data['isRadiant']
    for entry in match_data['players']:

        # Look for teammates
        if entry['isRadiant'] and player_is_radiant:
            # Add teammates' heroes' names to the list
            with_heroes.append(HERO_MAP[entry['hero_id']]['localized_name'])
            
            # If the teammate is in the friends list, add it to the list of friends played with
            if entry['account_id'] in FRIENDS_MAP.keys():
                with_friends.append(FRIENDS_MAP[entry['account_id']])
        
        # Look for enemies
        else:
            # Add enemies' heroes' names to the list
            against_heroes.append(HERO_MAP[entry['hero_id']]['localized_name'])
    
    last_game_state.with_heroes = tuple(with_heroes)
    last_game_state.with_friends = tuple(with_friends)
    last_game_state.against_heroes = tuple(against_heroes)

    # TODO: REMOVE THIS
    print('updated last-game state')


def generate_game_notification(last_game_state: LastGameState) -> str:
    hero = last_game_state.hero
    won_or_lost = 'won' if last_game_state.victory else 'lost'

    return f'Just {won_or_lost} a game as {hero}'


def generate_old_game_notification(last_game_state: LastGameState) -> str:
    hero = last_game_state.hero
    won_or_lost = 'won' if last_game_state.victory else 'lost'

    return f'I {won_or_lost} my last game as {hero}'


def dota_game_service(last_game_state: LastGameState):
    while True:
        if time.time() - last_game_state.last_query_time >= 10.:
            
            # TODO: REMOVE THIS
            print('time to check')

            if last_game_state.match_id > 0:
                try:
                    # Refresh the player's match data on OpenDota.com
                    refresh_response = requests.post(url=PLAYER_REFRESH_URL)

                    # Get the latest match data
                    match_id = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1}).json()[0]['match_id']

                    if match_id != last_game_state.match_id:
                        match_data = requests.get(url=MATCHES_URL + str(match_id)).json()

                        # Update the last game state with the new game's information
                        update_last_game_state(last_game_state, match_data)

                        # Post to the group chat
                        send_message(generate_game_notification(last_game_state))

                except:
                    pass

            else:
                # Get the latest match data
                match_id = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1}).json()[0]['match_id']
                print(f'Last match id: {match_id}')

                # Get the latest match data
                match_data = requests.get(url=MATCHES_URL + str(match_id)).json()

                # Give the last game state its data
                update_last_game_state(last_game_state, match_data)
            
            last_game_state.last_query_time = time.time()



if __name__ == '__main__':
    # db.create_all()

    manager = Manager()
    last_game_state = manager.Namespace()
    # last_game_state.database = db
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
