import vk_api
import datetime
from sqlalchemy.orm import session
from vk_api import VkApiError
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import db_functions, db_reboot, db_tables
from db_functions import add_prompt
import configparser
from keyboard import keyb
import random


config = configparser.ConfigParser()
config.read('config.ini')
token = config['VK']['group_token']

# TOKEN = 'vk1.a.pt524_volH1KULjGa3epiXZzczIcveDn8AbW0zm8l-91aowhUzuLBg5gVLFrdbnoItfRHm_BEV2YjtwwQlygElRUfAKKSOfcnM9ib7HeUn3Y9P4c3AuMUNIC7YRIMdKy2otm3eeK0jzWdsU9urRPt5I5mXvl4jK0txwdD6PoMllNk4mp8befU3kXMO6CmknhS4WzOxitBxFuyJ45Ik8F3A'

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send_message(user_id, message, attachments=None):
    vk.messages.send(user_id=user_id,
                     message=message,
                     keyboard=keyb.get_keyboard(),
                     random_id=random.getrandbits(64),
                     attachment=attachments)


def wait_for_response(user_id):
    """Функция для ожидания ответа от пользователя."""
    print(f"Ожидание ответа от пользователя {user_id}...")

    while True:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
                return event.text


def get_user_info(session, user_id):
    user_info = session.users.get(user_ids=user_id, fields='sex, city, bdate')[0]
    name = user_info.get('first_name', '') + ' ' + user_info.get('last_name', '')
    city = user_info.get('city', {}).get('title', 'Не указан')

    try:
        bdate = user_info.get('bdate', '')
        if bdate:
            now_date = datetime.date.today()
            age = now_date.year - datetime.datetime.strptime(bdate, '%d.%m.%Y').year
        else:
            age = "0"
    except Exception:
        age = '0'

    gender = user_info.get('sex', 0)
    if gender == 1:
        gender = ' женский'
    elif gender == 2:
        gender = ' мужской'
    else:
        gender = 'Не указан'

    return name, city, age, gender


def request_search_parameters(user_id, send_message):
    # Создаем словарь для хранения параметров поиска
    params = {}

    # Запрашиваем пол
    send_message(user_id, "Введи пол предполагаемой второй половинки")
    response = wait_for_response(user_id)

    while response.lower() not in ['мужской', 'женский']:
        send_message(user_id, "Я знаю только два пола: 'мужской' или 'женский'.")
        response = wait_for_response(user_id)

    params['gender'] = response.lower()

    # Запрашиваем возраст
    send_message(user_id, "Введи возраст предполагаемой второй половинки")
    response = wait_for_response(user_id)

    # Проверяем, является ли ответ числом
    while not response.isdigit() or int(response) < 0:
        send_message(user_id, "Введи возраст нормально, ну, не дурачок же")
        response = wait_for_response(user_id)

    params['age'] = response

    # Запрашиваем город
    send_message(user_id, "В каком городе ищем?")
    response = wait_for_response(user_id)

    # Сохраняем информацию о городе
    params['city'] = response.strip()

    # Возвращаем собранные параметры
    # print(params)
    return params


def get_photos(user_session, user_id):
    photos = user_session.method('photos.get', {
        'owner_id': user_id,
        'album_id': 'profile',
        'count': 100,
        'extended': 1,
        'v': 5.199
    })

    if 'items' not in photos or not photos['items']:
        return []

    sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
    top_photos = sorted_photos[:3]
    max_size_photos = []

    for photo in top_photos:
        max_size_photo = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
        max_size_photos.append({
            'url': max_size_photo['url'],  # URL самого большого изображения
            'owner_id': photo['owner_id'],
            'id': photo['id']
        })

    return max_size_photos


def find_candidates(user_session, gender, age, city):
    search_results = session.users.search(
        sex=gender,
        age_from=age,
        age_to=age,
        city=city,
        count=100  # количество кандидатов для поиска
    )

    candidates = []
    for user in search_results['items']:
        user_photos = get_photos(user['id'])
        candidates.append({
            'user_id': user['id'],
            'name': user['first_name'] + ' ' + user['last_name'],
            'photos': user_photos
        })

    return candidates








