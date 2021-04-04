import os
import time
from enum import Enum
from typing import List, NamedTuple

import requests
from common import send_message

HOUSTON_STEAM64 = '76561198057018373'

FRIENDS_MAP_64 = {
    '76561198081078910': 'Gavin',
    '76561198066957989': 'Blake',
    '76561198073250445': 'Grady',
    '76561198055815164': 'Kevin',
    '76561198093453221': 'Jake',
    '76561198015601592': 'Steve',
    '76561198087125563': 'Tony'
}

FRIEND_LIST = list(FRIENDS_MAP_64.values())

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM64_ID_LIST = ','.join(list(FRIENDS_MAP_64.keys()) + [HOUSTON_STEAM64])

STEAM_API_URL = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
STEAM_API_PARAMS = {'key': STEAM_API_KEY, 'steamids': STEAM64_ID_LIST}


class STEAM_STATUS_ENUM(Enum):
    OFFLINE = 0
    ONLINE = 1
    BUSY = 2
    AWAY = 3


STEAM_STATUS_TEXT_MAP = {
    0: 'offline',
    1: 'online',
    2: 'busy',
    3: 'away'
}


def get_friends_online() -> List[str]:
    response = requests.get(url=STEAM_API_URL, params=STEAM_API_PARAMS)

    data = response.json()['response']['players']

    friends_online = []
    houston_online = False
    for entry in data:
        if entry['personastate'] == 1:
            if entry['steamid'] == HOUSTON_STEAM64:
                houston_online = True
            else:
                friends_online.append(FRIENDS_MAP_64[entry['steamid']])

    if houston_online:
        friends_online.append('I')

    return friends_online


def generate_friends_online_message() -> str:
    friends_online = get_friends_online()

    if not len(friends_online):
        return 'Nobody is online'

    if len(friends_online) > 2:
        friend_list = list(friends_online[:-1]) + ['and ' + friends_online[-1]]
        friends_string = ', '.join(friend_list)
        return f"{friends_string} are online"

    if len(friends_online) == 2:
        return f'{friends_online[0]} and {friends_online[1]} are online'

    return f'Just {friends_online[0]} is online'


class FriendsOnlineState(NamedTuple):

    last_update_time: float

    Gavin: int
    Blake: int
    Grady: int
    Kevin: int
    Jake: int
    Steve: int
    Tony: int
    Houston: int


def update_friends_online_state(state: FriendsOnlineState, announce: bool = False):
    response = requests.get(url=STEAM_API_URL, params=STEAM_API_PARAMS)

    data = response.json()['response']['players']

    for entry in data:
        # Special case for Houston
        if entry['steamid'] == HOUSTON_STEAM64:

            # Compare Houston's previous and current statuses
            houston_prev_state = state.Houston
            houston_curr_state = entry['personastate']
            if houston_prev_state != houston_curr_state:

                # If they are different, then update and send a message about the change
                state.Houston = houston_curr_state
                if announce:
                    send_message(f'I am now {houston_curr_state}')


        else:
            friend = FRIENDS_MAP_64[entry['steamid']]

            # Compare the friend's previous and current statuses
            friend_prev_state = state.__getattribute__(friend)
            friend_curr_state = entry['personastate']
            if friend_prev_state != friend_curr_state:
                
                # If they are different, then update and send a message about the change
                state.__setattr__(friend, friend_curr_state)
                if announce:
                    send_message(f'{friend} is now {STEAM_STATUS_TEXT_MAP[friend_curr_state]}')


def online_status_service(loop: bool):
    state = FriendsOnlineState(-1, -1, -1, -1, -1, -1, -1, -1, -1)

    # Get the current state without announcing it
    update_friends_online_state(state, False)
    state.last_update_time = time.time()

    while loop:
        if time.time() - state.last_update_time >= 2.:
            update_friends_online_state(state, True)
            state.last_update_time = time.time()