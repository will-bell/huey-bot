import os
import time
from typing import NamedTuple, Tuple, Dict

import requests
from common import send_message_as_huey

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
    126859835: 'Tony'
}

FRIENDS_ID_LIST = list(FRIENDS_MAP.keys())
ALL_ID_LIST = [PLAYER_ID] + FRIENDS_ID_LIST


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
    houstons_GPM: int
    friends_deaths: Dict[str, int]


def make_last_game_state_args(match_data: dict) -> tuple:
    # Fill out the match data fields
    match_id = match_data['match_id']
    start_time = match_data['start_time']

    player_data = None
    for entry in match_data['players']:
        if entry['account_id']:
            if int(entry['account_id']) == PLAYER_ID:
                player_data = entry
                break

    side = 'Radiant' if player_data['isRadiant'] else 'Dire'
    victory = bool(player_data['win'])
    duration = int(player_data['duration'] / 60)

    # Fill out the player data fields for Houston
    hero = HERO_MAP[player_data['hero_id']]['localized_name']
    kills = player_data['kills']
    deaths = player_data['deaths']
    assists = player_data['assists']
    player_gpm = player_data['gold_per_min']

    # Find heroes on either side and friends
    with_heroes = []
    against_heroes = []
    with_friends = []

    # Keep track of friends' deaths
    friends_deaths = {}

    player_is_radiant = player_data['isRadiant']
    for entry in match_data['players']:

        # Look for teammates
        if entry['isRadiant'] == player_is_radiant:
            # Add teammates' heroes' names to the list
            with_heroes.append(HERO_MAP[entry['hero_id']]['localized_name'])

            # If the teammate is in the friends list, add it to the list of friends played with
            if entry['account_id'] in FRIENDS_MAP.keys():
                friend = FRIENDS_MAP[entry['account_id']]
                with_friends.append(friend)

                # Also get the number of deaths for fun later
                friends_deaths[friend] = entry['deaths']

        # Look for enemies
        else:
            # Add enemies' heroes' names to the list
            against_heroes.append(HERO_MAP[entry['hero_id']]['localized_name'])

    with_heroes = tuple(with_heroes)
    with_friends = tuple(with_friends)
    against_heroes = tuple(against_heroes)

    return time.time(), match_id, start_time, side, victory, duration, hero, kills, deaths, assists, with_heroes, \
        with_friends, against_heroes, player_gpm, friends_deaths


def update_last_game_state(last_game_state: LastGameState, match_data: dict):
    last_query_time, match_id, start_time, side, victory, duration, hero, kills, deaths, assists, with_heroes, \
        with_friends, against_heroes, player_gpm, friends_deaths = make_last_game_state_args(match_data)

    last_game_state.last_query_time = last_query_time
    last_game_state.match_id = match_id
    last_game_state.start_time = start_time
    last_game_state.side = side
    last_game_state.victory = victory
    last_game_state.duration = duration
    last_game_state.hero = hero
    last_game_state.kills = kills
    last_game_state.deaths = deaths
    last_game_state.assists = assists
    last_game_state.with_heroes = with_heroes
    last_game_state.with_friends = with_friends
    last_game_state.against_heroes = against_heroes
    last_game_state.houstons_GPM = player_gpm
    last_game_state.friends_deaths = friends_deaths


def generate_game_notification(last_game_state: LastGameState) -> str:
    hero = last_game_state.hero
    won_or_lost = 'won' if last_game_state.victory else 'lost'

    return f'Just {won_or_lost} a game as {hero}'


def generate_player_gpm(last_game_state: LastGameState) -> str:
    player_gpm = last_game_state.houstons_GPM

    return str(player_gpm)


def generate_old_game_notification(last_game_state: LastGameState) -> str:
    hero = last_game_state.hero
    won_or_lost = 'won' if last_game_state.victory else 'lost'

    kills = last_game_state.kills
    deaths = last_game_state.deaths
    assists = last_game_state.assists

    friends_deaths = last_game_state.friends_deaths
    high_score = -1
    feeder = ''
    for friend, deaths in friends_deaths.items():
        if deaths > high_score:
            feeder = friend
            high_score = deaths

    if deaths > high_score:
        feeder = 'I'
        high_score = deaths

    most_deaths = f"{feeder} had the most deaths with {high_score} deaths. Oof"

    with_friends = ''
    if len(last_game_state.with_friends) == 1:
        with_friends = f' with {last_game_state.with_friends[0]}'

    elif len(last_game_state.with_friends) > 2:
        friend_list = list(last_game_state.with_friends[:-1]) + ['and ' + last_game_state.with_friends[-1]]
        with_friends = ' with ' + ', '.join(friend_list)

    elif len(last_game_state.with_friends) == 2:
        with_friends = f' with {last_game_state.with_friends[0]} and {last_game_state.with_friends[1]}'

    return \
        f'I {won_or_lost} my last game as {hero}{with_friends}. My KDA was {kills}/{deaths}/{assists}. {most_deaths}.'


def get_last_match_data() -> LastGameState:
    # Refresh the player's match data on OpenDota.com
    _ = requests.post(url=PLAYER_REFRESH_URL)
    time.sleep(.2)

    # Get the latest match data
    match_id = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1}).json()[0]['match_id']
    match_data = requests.get(url=MATCHES_URL + str(match_id)).json()

    return LastGameState(*make_last_game_state_args(match_data))


def dota_game_service(last_game_state: LastGameState):
    while True:
        if time.time() - last_game_state.last_query_time >= 60.:
            if last_game_state.match_id > 0:
                # Refresh the player's match data on OpenDota.com
                _ = requests.post(url=PLAYER_REFRESH_URL)

                time.sleep(.2)

                # Get the latest match data
                response = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1})

                if response.status_code == 200:
                    match_id = response.json()[0]['match_id']

                    if match_id != last_game_state.match_id:
                        match_data = requests.get(url=MATCHES_URL + str(match_id)).json()

                        # Update the last game state with the new game's information
                        update_last_game_state(last_game_state, match_data)

                        # Post to the group chat
                        send_message_as_huey(generate_game_notification(last_game_state))

                    else:
                        last_game_state.last_query_time = time.time()

            else:
                # Get the latest match data
                response = requests.get(url=PLAYER_MATCHES_URL, params={'limit': 1})

                if response.status_code == 200:
                    match_id = response.json()[0]['match_id']

                    # Get the latest match data
                    match_data = requests.get(url=MATCHES_URL + str(match_id)).json()

                    # Give the last game state its data
                    update_last_game_state(last_game_state, match_data)
