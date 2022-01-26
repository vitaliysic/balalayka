#r-
#t-
#f-
#


#Комплектация библиотек

import requests
#сделать HTTP-запросы
import random
#Генератор псевдослучайных чисел для различных дистрибутивов
import math
#Доступ к математическим функциям

#из библиотеки для webrtc используем протоколы для описания ice кондиданта и описания соединения между нами и сервером
from aiortc import RTCPeerConnection, RTCSessionDescription
#Использование медиа потока,транслировать медиа поток, трансляция медиа через сервер
from aiortc.contrib.media import MediaPlayer, MediaRelay

#Соединение с сервером ома
domain = 'omegle.com'
#Сервера для работы 
serverList = ["front1", "front2", "front3", "front4", "front5", "front6", "front7", "front8", "front9", "front10",
              "front11", "front12", "front13", "front14", "front15", "front16", "front17", "front18", "front19",
              "front20", "front21", "front22", "front23", "front24", "front25", "front26", "front27", "front28",
              "front29", "front30", "front31", "front32", "front33", "front34", "front35", "front36", "front37",
              "front38", "front39", "front40", "front41", "front42", "front43", "front44", "front45", "front46",
              "front47", "front48"]

#Создать динамичный айди
def new_rand_id():
    rand_id = ''
    alphabet = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    #Способы инициализации списка алфавитов
    for _ in range(0, 8):
        #Формула для получения айди.(Формула уникальна для каждого сервера?)
        rand_id += alphabet[math.floor(random.uniform(0, 1) * len(alphabet))]
    #Айди получен 
    return rand_id

#
def nocache():
    return random.uniform(0, 1)

#
def get_origin():
    return f'https://{serverList[random.randint(0, len(serverList) - 1)]}.{domain}'

#Выполнение (Имитация выполнения) событий через браузер
def event_dispatch(events):
    for event in events:
        exit()

#(Поиск кнопки видео (???))
def on_track_handler(data):
    if data.track.kind == 'video':
        print(data.stream[0])

# C данного момента,  выполнять циклично

if __name__ == '__main__':
#Подключение к прокси
    proxies = {
        'https': 'https://45.167.253.129:999',
    }

    s = requests.Session()
    s.proxies = proxies
    
    origin = get_origin()

    #Параметры курл пакета
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'}
    #Передать параметр динамичного айди
    randId = new_rand_id()
    #Передача параметров. Блокировка кеша, рандомный айди
    params = {
        'nocache': nocache(),
        'randid': randId
    }
    #Сборка курл пакетов для подключения
    url = f'{origin}/status'
    r = s.get(url=url, headers=headers, params=params)
    r = r.json()
    #Если не не получилось, прекратить запросы
    if len(r) == 0:
        print('status fail')
        exit()

    serverList = r['servers']
    origin = get_origin()
    
    # Цикл пока верно
    while True:
        #Запрос параметра- Ответ серверу
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
        #отправка курл пакетов на сервер
        url = f'{origin}/start'
        #
        r = s.post(url=url, headers=headers, params=params)
        r = r.json()
        #
        if len(r) == 0:
            print('start fail')
            exit()

        #Получить клиент айди
        clientId = r['clientID']
        #Отправка клиент айди
        data = {
            'id': clientId
        }
        url = f'{origin}/events'
        
        #Проверка сообщения от ом.вип
        while True:
            r = s.post(url=url, headers=headers, data=data)
            r = r.json()

            print(r)
             #Если получили сообщение омегл, переключить собеседника
            if r is None or len(r) > 0 and r[0][0] == 'gotMessage' and 'OMEGLE' in r[0][1]:
                url = f'{origin}/disconnect'
                s.post(url=url, headers=headers, data=data)
                break
        #Если не получили данные от собеседника
        if r is None or not 'rtcpeerdescription' in r:
            continue

        index = r.index('rtcpeerdescription')

        offer = RTCSessionDescription(sdp=r[index]["sdp"], type=r[index]["type"])

        pc = RTCPeerConnection()
        
        pc.setRemoteDescription(offer)

        #Назначить дырку
        player = MediaPlayer('v.mp4')

        #Вывести в консоль.данные собеседника
        for t in pc.getTransceivers():
            print("")
            print("")
            print("")
            print(t)
            print("")
            print("")
            print("")

            #
            if t.kind == "audio":
                pc.addTrack(player.audio)
            elif t.kind == "video":
                pc.addTrack(player.video)
        #
        answer = pc.createAnswer()
        #
        pc.setLocalDescription(answer)

        pc.add_listener('track', on_track_handler)
        
        #Если отсутствует или некорректный ice собеседника=пропустить
        if not 'icecandidate' in r:
            while not 'icecandidate' in r:
                url = f'{origin}/events'
                r = s.post(url=url, headers=headers, data=data)
                r = r.json()
                print(r)
                #
                if r is None:
                    url = f'{origin}/disconnect'
                    s.post(url=url, headers=headers, data=data)
                    break

        if not 'icecandidate' in r:
            continue

        url = f'{origin}/rtcpeerdescription'
        data = {
            'desc': '{"type":"' + pc.localDescription.type + ',"sdp":"' + pc.localDescription.sdp + '"}',
            'id': randId
        }
        r = s.post(url=url, headers=headers, data=data)
        r = r.text

        print(r)

        url = f'{origin}/icecandidate'

        
        
