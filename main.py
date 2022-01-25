import requests
import random
import math


serverList = ["front1", "front2", "front3", "front4", "front5", "front6", "front7", "front8", "front9", "front10",
              "front11", "front12", "front13", "front14", "front15", "front16", "front17", "front18", "front19",
              "front20", "front21", "front22", "front23", "front24", "front25", "front26", "front27", "front28",
              "front29", "front30", "front31", "front32", "front33", "front34", "front35", "front36", "front37",
              "front38", "front39", "front40", "front41", "front42", "front43", "front44", "front45", "front46",
              "front47", "front48"]


def new_rand_id():
    rand_id = ''
    alphabet = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    for i in range(0, 8):
        rand_id += alphabet[math.floor(random.uniform(0, 1) * len(alphabet))]
    return rand_id


def nocache():
    return random.uniform(0, 1)


def get_origin():
    return f'https://{serverList[random.randint(0, len(serverList) - 1)]}.{domain}'


if __name__ == '__main__':
    domain = 'omegle.com'
    origin = get_origin()

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}

    randId = new_rand_id()

    params = {
        'nocache': nocache(),
        'randid': randId
    }
    url = f'{origin}/status'
    r = requests.get(url=url, headers=headers, params=params)
    r = r.json()

    print(r)

    serverList = r['servers']
    origin = get_origin()

    params = {
        'caps': 'recaptha2,t',
        'firstevents': '1',
        'spid': '',
        'randid': randId,
        'group': 'unmon',
        'lang': 'en',
        'camera': 'Camera',
        'webrtc': '1'
    }
    url = f'{origin}/start'
    r = requests.post(url=url, headers=headers, params=params)
    r = r.json()

    print(r)

    clientId = r['clientID']

    data = {
        'id': clientId
    }
    url = f'{origin}/events'
    r = requests.post(url=url, headers=headers, data=data)
    r = r.json()

    print(r)

    r = requests.post(url=url, headers=headers, data=data)
    r = r.json()

    print(r)
