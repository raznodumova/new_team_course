import vk_api
import configparser
import datetime

from sqlalchemy import event
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import datetime


def user_token():
    config = configparser.ConfigParser()
    config.read('config.ini')
    user_token = config['VK']['user_token']
    # print(user_token)
    return user_token


def group_token():
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['VK']['group_token']
    return token


def get_user_name(user_id):
    vk_session = vk_api.VkApi(token=user_token)
    vk = vk_session.get_api()
    name = vk.users.get(user_id=user_id)[0]['first_name']
    last_name = vk.users.get(user_id=user_id)[0]['last_name']
    full_name = name + ' ' + last_name
    return full_name


def get_user_city(user_id):
    vk_session = vk_api.VkApi(token=user_token)
    vk = vk_session.get_api()
    city = vk.users.get(user_id=user_id)[0]['city']['title']
    return city


def get_user_age(user_id):
    vk_session = vk_api.VkApi(token=user_token)
    vk = vk_session.get_api()
    now_date = datetime.datetime.now()
    age = vk.users.get(user_id=user_id)[0]['bdate']
    user_age = now_date.year - int(age[6:10])
    return user_age


def get_gender(user_id):
    vk_session = vk_api.VkApi(token=user_token)
    vk = vk_session.get_api()
    gender = vk.users.get(user_id=user_id)[0]['sex']
    if gender == 1:
        gender = 'Женщина'
    else:
        gender = 'Мужчина'
    return gender


def change_gender(user_id):
    vk_session = vk_api.VkApi(token=user_token)
    vk = vk_session.get_api()
    sex = vk.users.get(user_id=user_id)[0]['sex']
    if sex == 1:
        sex = 2
    else:
        sex = 1


def get_user_photo(user_id):
    vk_session = vk_api.VkApi(token=group_token)
    vk = vk_session.get_api()
    photos = vk.method('photos.get', {
            'owner_id': user_id,
            'album_id': 'profile',  # Получаем фотографии из профиля
            'count': 100,  # Максимально возможное количество (опять же 100)
            'extended': 1,  # Чтобы получить дополнительную информацию о фото
            'v': 5.199
        })
    if 'items' not in photos or not photos['items']:
        return []

    # Сортируем фотографии по количеству лайков
    sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)

    # Берем три самые популярные фотки
    top_photos = sorted_photos[:3]

    # Получаем фотки с наибольшими размерами
    max_size_photos = []
    for photo in top_photos:
        max_size_photo = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
        max_size_photos.append(max_size_photo['url'])  # URL самого большого изображения

    return max_size_photos


def wrt_msg(user_id, message):
    token = group_token()
    vk_session = vk_api.VkApi(token)
    vk = vk_session.get_api()
    vk.messages.send(user_id=user_id, message=message)


if __name__ == '__main__':
    user_token()