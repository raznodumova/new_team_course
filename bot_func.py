import vk_api
import datetime
from sqlalchemy.orm import session
from vk_api import VkApiError
from vk_api.longpoll import VkLongPoll, VkEventType
import requests

import db_tables
from db_tables import UserPrompt
from db_functions import add_prompt, create_user, s, find_prompt, get_prompt
import configparser
from keyboard import keyb_for_search, keyb_for_start
import random



config = configparser.ConfigParser()
config.read('config.ini')
token = config['VK']['group_token']

vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def send_message(user_id, message, keyboard=None, attachments=None):
    vk.messages.send(user_id=user_id,
                     message=message,
                     keyboard=keyb_for_start.get_keyboard() if keyboard is None else keyb_for_search.get_keyboard(),
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
            age = bdate if bdate else 'Не указан'
    except Exception:
        age = 'Не указан'

    gender = user_info.get('sex', 0)

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
        if response == 'мужской':
            params['gender'] = 2
        elif response == 'женский':
            params['gender'] = 1

    # запрашиваем возраст
    send_message(user_id, "Введи возраст предполагаемой второй половинки")
    response = wait_for_response(user_id)
    # Проверяем, является ли ответ числом
    while not response.isdigit() or int(response) < 18:
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
    prompt = UserPrompt(user_id=user_id,
                        city_for_search=params["city"],
                        gender_for_search=params["gender"],
                        age_for_search=params["age"])
    add_prompt(prompt)
    print(params.values())
    return params


def get_photos(user_session, user_id):
    photos = user_session.photos.get(
        owner_id=user_id,
        album_id="profile",
        count=100,
        extended=1,
        v=5.199
    )

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
    search_results = user_session.users.search(
        sex=gender,
        age_from=age,
        age_to=age,
        hometown=city,
        count=100,
        status='1' or '6',
        has_photo=1)  # количество кандидатов для поиска
    candidates = []
    for user in search_results['items']:
        user_id = user['id']
        photos = get_photos(user_session, user_id)

        candidates.append({
            'user_id': user['id'],
            'name': user['first_name'] + ' ' + user['last_name'],
            'photos': photos
        })

    return candidates


def handle_start_command(user_id, vk, user_session):
    msg = 'Привет, братишка! Мы придумали для тебя кнопочки, чтобы тебе было легче ориентироваться'
    send_message(user_id, msg)

    main_user = get_user_info(vk, user_id)
    user = db_tables.User(user_id=user_id, name=main_user[0], city=main_user[1], age=main_user[2], gender=main_user[3])

    create_user(user)
    s.commit()

    def from_01_to_text(gender_code):
        if gender_code == 1:
            return 'женский'
        elif gender_code == 2:
            return 'мужской'
        else:
            return 'Не указан'

    msg_two = (f'Тебя зовут: {main_user[0]}\n'
               f'Ты из: {main_user[1]}\n'
               f'Твой возраст: {main_user[2]} \n'
               f'Твой пол: {from_01_to_text(main_user[3])}')
    send_message(user_id, msg_two)

    msg_three = 'Вот твои самые классные фотки'
    send_message(user_id, msg_three)

    top_photos = get_photos(user_session, user_id)
    photo_attachments = [f"photo{photo['owner_id']}_{photo['id']}" for photo in top_photos]

    if photo_attachments:
        attachments = ','.join(photo_attachments)
        send_message(user_id, msg_three, attachments=attachments)


def handle_search_command(user_id, user_session, send_message):
    if find_prompt(user_id) == str(user_id):
        params = get_prompt(user_id)
    else:
        msg = 'Ну давай'
        send_message(user_id, msg)
        params = request_search_parameters(user_id, send_message)
        prompt = UserPrompt(user_id=user_id,
                            gender_for_search=params['gender'],
                            city_for_search=params['city'],
                            age_for_search=params['age'])
        add_prompt(prompt)

    candidates = find_candidates(user_session, gender=params['gender'], city=params['city'], age=params['age'])

    msg = ('Чтобы посмотреть следующего кандидата, нажми кнопку "Следующий"\n'
           'Чтобы добавить кандидата в ЧС, нажми на кнопку "Добавить в ЧС"\n'
           'Чтобы добавить кандидата в избранное, нажми на кнопку "Добавить в избранное"\n')
    send_message(user_id, msg, keyboard=keyb_for_start.get_keyboard())

    current_candidate_index = 0

    while current_candidate_index < len(candidates):
        person = candidates[current_candidate_index]
        send_message(user_id, f'{person["name"]}  https://vk.com/id{person["user_id"]}',
                     keyboard=keyb_for_search.get_keyboard())

        # Обработка добавления фотографий
        photo_attachments = []
        for photo in person["photos"]:
            attachment = f"photo{photo['owner_id']}_{photo['id']}"
            photo_attachments.append(attachment)

        if photo_attachments:
            attachments = ','.join(photo_attachments)
            send_message(user_id, "Вот фотки", attachments=attachments,
                         keyboard=keyb_for_search.get_keyboard())

        us_msg = wait_for_response(user_id)

        # Обработка нажатий кнопок
        if us_msg == 'Следующий':
            current_candidate_index += 1  # Переход к следующему кандидату
            print(current_candidate_index)

            if current_candidate_index >= len(candidates):
                send_message(user_id, 'Это последний кандидат', keyboard=keyb_for_search.get_keyboard())
                current_candidate_index = len(candidates) - 1  # Остаёмся на последнем кандидате






