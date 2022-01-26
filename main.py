import requests
import random
import math

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay

domain = 'omegle.com'
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
    subdomain = serverList[random.randint(0, len(serverList) - 1)]
    state['subdomain'] = subdomain
    return f'https://{subdomain}.{domain}'


state = {
    'session': None,
    'subdomain': '',
    'origin': '',
    'randId': '',
    'clientId': '',
    'rtcpeerdescription': '',
    'messages': [],
    'pc': None
}


def update():
    if state['subdomain'] not in serverList:
        state["origin"] = get_origin()


def events_dispatch(new_events):
    if new_events is None:
        return []
    event_list = []
    for event in new_events:
        if event[0] == 'waiting':
            event_list.append('waiting')
        elif event[0] == 'gotMessage':
            event_list.append('gotMessage')
            state['messages'].append(event[1])
        elif event[0] == 'error':
            event_list.append('error')
        elif event[0] == 'rtcpeerdescription':
            event_list.append('rtcpeerdescription')
            state['rtcpeerdescription'] = event[1]
        elif event[0] == 'strangerDisconnected':
            event_list.append('strangerDisconnected')
        elif event[0] == 'statusInfo':
            event_list.append('statusInfo')
            serverList.clear()
            serverList.append(event[1]['servers'])
            update()
    return event_list


def contains_in_messages(phrase):
    for message in state['messages']:
        if phrase in message:
            return True
    return False


def send_request(req_type):
    origin = state['origin']
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    params = {}
    data = {}
    url = ''
    s = state['session']
    response = {}
    clientId = state['clientId']
    if req_type == 'status':
        params = {
            'nocache': nocache(),
            'randid': randId
        }
        url = f'{origin}/status'
        response = s.get(url=url, headers=headers, params=params)
        response = response.json()
        return response
    elif req_type == 'start':
        params = {
            'caps': 'recaptha2,t',
            'firstevents': '1',
            'spid': '',
            'randid': state['randId'],
            'group': 'unmon',
            'lang': 'en',
            'camera': 'Camera HD',
            'webrtc': '1'
        }
        url = f'{origin}/start'
    elif req_type == 'events':
        data = {
            'id': clientId
        }
        print(clientId)
        url = f'{origin}/events'
    elif req_type == 'disconnect':
        data = {
            'id': clientId
        }
        url = f'{origin}/disconnect'
        response = s.post(url=url, headers=headers, params=params, data=data)
        return response.text
    elif req_type == 'rtcpeerdescription':
        url = f'{origin}/rtcpeerdescription'
        pc = state['pc']
        data = {
            'desc': '{"type":"' + pc.localDescription.type + ',"sdp":"' + pc.localDescription.sdp + '"}',
            'id': clientId
        }
        response = s.post(url=url, headers=headers, params=params, data=data)
        return response.text
    elif req_type == 'icecandidate':
        pass

    response = s.post(url=url, headers=headers, params=params, data=data)
    response = response.json()

    return response


if __name__ == '__main__':

    proxies = {
        'https': 'https://49.233.173.151:9080',
    }

    state['session'] = requests.Session()
    state['session'].proxies = proxies

    state["randId"] = new_rand_id()
    randId = state["randId"]

    update()

    print(f"origin: {state['origin']}\nrandId: {randId}")

    r = send_request('status')

    if len(r) == 0:
        print('status fail')
        exit()

    print(f"Online: {r['count']}")
    serverList = r['servers']
    update()

    while True:
        r = send_request('start')

        if len(r) == 0:
            print('start fail')
            exit()

        if 'events' in r:
            events = events_dispatch(r['events'])
            if 'error' in events:
                print('Banned')
                exit()

        state['clientId'] = r['clientID']
        clientId = state['clientId']

        print(f"clientId: {state['clientId']}")

        while True:
            r = send_request('events')

            print(r)
            events = events_dispatch(r)

            if contains_in_messages('OMEGLE'):
                send_request('disconnect')
                break

        if len(events) == 0 or 'rtcpeerdescription' not in r:
            continue

        print("")
        print("")
        print("")
        print(f"{state['rtcpeerdescription']}")
        print("")
        print("")
        print("")
        
        offer = RTCSessionDescription(sdp=state['rtcpeerdescription']["sdp"], type=state['rtcpeerdescription']["type"],)
        
        state['pc'] = RTCPeerConnection()
        pc = state['pc']
        
        pc.setRemoteDescription(offer)
        
        player = MediaPlayer('v.mp4')
        
        for t in pc.getTransceivers():
            print("")
            print("")
            print("")
            print(t)
            print("")
            print("")
            print("")
            if t.kind == "audio":
                pc.addTrack(player.audio)
            elif t.kind == "video":
                pc.addTrack(player.video)
        
        answer = pc.createAnswer()
        pc.setLocalDescription(answer)
        
        if 'icecandidate' not in r:
            while 'icecandidate' not in r:
                r = send_request('events')
        
                print(r)
        
                if len(r) == 0:
                    send_request('disconnect')
                    break
        
        if 'icecandidate' not in r:
            continue
        
        
        r = r.text
        
        print(r)
