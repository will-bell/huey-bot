import requests
from typing import List
import os


FRIENDS_MAP_64 = {
    '76561198057018373': 'Houston',
    '76561198081078910': 'Gavin',
    '76561198066957989': 'Blake',
    '76561198073250445': 'Grady',
    '76561198055815164': 'Kevin',
    '76561198093453221': 'Jake',
    '76561198015601592': 'Steve',
    '76561198087125563': 'Tony'
}

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
STEAM64_ID_LIST = ','.join(list(FRIENDS_MAP_64.keys()))

STEAM_API_URL = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'
STEAM_API_PARAMS = {'key': STEAM_API_KEY, 'steamids': STEAM64_ID_LIST}


def get_friends_online() -> List[str]:
    response = requests.get(url=STEAM_API_URL, params=STEAM_API_PARAMS)

    data = response.json()['response']['players']

    friends_online = []
    for entry in data:
        if entry['personastate'] == 1:
            friends_online.append(FRIENDS_MAP_64[entry['steamid']])

    return friends_online


def generate_friends_online_message() -> str:
    friends_online = get_friends_online()

    if not len(friends_online):
        return 'Nobody is online'

    if len(friends_online) > 2:
        friend_list = list(friends_online[:-1]) + ['and ' + friends_online[-1]]
        friends_string = ','.join(friend_list)
        return f"{friends_string} are online"

    if len(friends_online) == 2:
        return f'{friends_online[0]} and {friends_online[1]} are online'

    return f'Just {friends_online[0]} is online'