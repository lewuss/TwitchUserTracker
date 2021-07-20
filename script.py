import requests, json, sys
from urllib.parse import quote

BASE_URL = 'https://api.twitch.tv/helix/'
authURL = 'https://id.twitch.tv/oauth2/token'

CLIENT_ID = ''
token = ''


AutParams = {'client_id': CLIENT_ID,
             'client_secret': token,
             'grant_type': 'client_credentials'
             }

AUTCALL = requests.post(url=authURL, params=AutParams)
ACCESS_TOKEN = AUTCALL.json()['access_token']
HEADERS = {'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + ACCESS_TOKEN}

INDENT = 2


def get_all_follows(user_id):
    pagination = ""
    Follows = []
    while True:
        query = get_follows_query(user_id, pagination)
        response = get_response(query)
        response_json = response.json()
        length = len(response_json['data'])

        for x in range(length):
            try:
                Follows.append(response_json['data'][x]['to_id'])
            except:
                Sadge = 1
        try:
            pagination = response_json['pagination']['cursor']
        except:
            return Follows


def print_response(response):
    response_json = response.json()
    print_response = json.dumps(response_json, indent=INDENT)
    print(print_response)


def get_response(query):
    url = BASE_URL + query
    response = requests.get(url, headers=HEADERS)
    return response


def get_stream_info_query(user_login):
    return 'streams?user_login={0}'.format(user_login)


def get_stream_info_query_from_list(users):
    query = 'streams?'
    for user in users:
        query += "user_id=" + quote(user) + "&"
    return query[:-1]


def get_user_query(user_login):
    return 'users?login={0}'.format(user_login)


def get_top_streams_query(language):
    return 'streams?first=100&language={0}'.format(language)


def get_follows_query(user_login, pagination):
    user_id = get_user_id(user_login)
    return 'users/follows?from_id={0}&first=100&after={1}'.format(user_id, pagination)


def check_if_live(user_ids):
    query = get_stream_info_query_from_list(user_ids)
    response = get_response(query)
    response_json = response.json()
    try:
        data = response_json['data']
        return [x['user_login'] for x in data if x['type'] == 'live']
    except:
        return []


def chunks(l, n):
    n = max(1, n)
    return (l[i:i + n] for i in range(0, len(l), n))


def get_live_from_follows(follows):
    live_follows = []
    tmp_list = chunks(follows, 100)
    for user_ids in tmp_list:
        live_follows += (check_if_live(user_ids))
    return live_follows


def get_top_streams_names():
    streams = []
    languages = ["pl","en"]
    for language in languages:
        query = get_top_streams_query(language)
        response = get_response(query)
        response_json = response.json()
        for x in range(99):
            name = response_json['data'][x]['user_login']
            streams.append(name)
    return streams


def merge_list(first_list, second_list):
    return set(first_list + second_list)


def get_user_id(user_login):
    query = get_user_query(user_login)
    response = get_response(query)
    response_json = response.json()
    try:
        User_ID = response_json['data'][0]['id']
        return (User_ID)
    except:
        Sadge = 1


def get_all_chatters(channel):
    url = f'http://tmi.twitch.tv/group/user/{channel.lower()}/chatters'
    try:
        all_chatters = requests.get(url).json()['chatters']
        chatters = all_chatters['staff'] + all_chatters['global_mods'] + all_chatters['admins'] \
                   + all_chatters['moderators'] + all_chatters['vips'] + all_chatters['viewers']
        chatters = sorted(chatters)
        return chatters
    except:
        print(channel)

def check_if_user_in_channel(user):
    top_streams = get_top_streams_names()
    follows = get_live_from_follows(get_all_follows(user))
    merged = merge_list(top_streams, follows)
    for channel in merged:
        chatters = get_all_chatters(channel)
        if user in chatters:
            print(user + " is in " + channel)


user = input().lower()
check_if_user_in_channel(user)
