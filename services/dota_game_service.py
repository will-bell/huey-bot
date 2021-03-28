import os
import time
from multiprocessing import Manager
from typing import Dict, List, NamedTuple

from app import send_message
from interaction.conversation import oi_huey
import requests


API_URL = "https://api.opendota.com/api/"

HERO_DATA_URL = API_URL + 'heroes'
hero_data_json = requests.get(url=HERO_DATA_URL).json()
HERO_MAP = {}
for entry in hero_data_json:
    HERO_MAP[entry['id']] = entry

PLAYER_ID = os.getenv('PLAYER_ID')
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
    with_heroes: List[str]
    with_friends: List[str]

    # Enemies
    against_heroes: List[str]


def update_last_game_state(last_game_state: LastGameState, match_data: Dict[str]):
    # Fill out the match data fields
    last_game_state.match_id = match_data['match_id']
    last_game_state.start_time = match_data['start_time']

    player_data = None
    
    for entry in match_data['players']:
        if entry['account_id'] == PLAYER_ID:
            player_data = entry
    
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



def generate_game_notification(last_game_state: LastGameState) -> str:
    hero = last_game_state.hero
    won_or_lost = 'won' if last_game_state.victory else 'lost'

    return f'Just {won_or_lost} a game as {hero}'


def dota_game_service(last_game_state: LastGameState):
    if time.time() - last_game_state.last_query_time >= 60.:
        if last_game_state.match_id > 0:
            try:
                # Refresh the player's match data on OpenDota.com
                refresh_response = requests.post(url=PLAYER_REFRESH_URL)

                # Get the latest match data
                match_id = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1}).json()[0]['match_id']

                if match_id != last_game_state.match_id:
                    match_data = requests.get(url=MATCHES_URL + str(match_id))

                    # Update the last game state with the new game's information
                    update_last_game_state(last_game_state, match_data)

                    # Post to the group chat
                    send_message(generate_game_notification(last_game_state))

            except:
                pass

        else:
            # Get the latest match data
            match_id = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1}).json()[0]['match_id']

            # Get the latest match data
            match_data = requests.get(url=MATCHES_URL + str(match_id))

            # Give the last game state its data
            update_last_game_state(last_game_state, match_data)
        
        last_game_state.last_query_time = time.time()
