import db_functions
from db_functions import *
import db_reboot

import db_tables
from bot_func import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
import configparser
from keyboard import keyb_for_start, keyb_for_search


config = configparser.ConfigParser()
config.read('config.ini')


def main():
    vk_session = vk_api.VkApi(token=config['VK']['group_token'])
    longpoll = VkLongPoll(vk_session)

    user_session = vk_api.VkApi(token=config['VK']['user_token']).get_api()

    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            text = event.text.lower()

            if text == 'начать':
                msg = 'Привет, братишка! Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
                send_message(user_id, msg)
                main_user = get_user_info(vk, user_id)
                user = db_tables.User(user_id=user_id, name=main_user[0], city=main_user[1], age=main_user[2], gender=main_user[3])
                db_functions.create_user(user)

                msg_two = (f'Тебя зовут: {main_user[0]}\n'
                           f'Ты из: {main_user[1]}\nТвой возраст: {main_user[2]} лет\nТвой пол: {main_user[3]}')
                send_message(user_id, msg_two)

                msg_three = 'Вот твои самые классные фотки'
                send_message(user_id, msg_three)

                top_photos = get_photos(user_session, user_id)
                photo_attachments = []
                for photo in top_photos:
                    attachment = f"photo{photo['owner_id']}_{photo['id']}"
                    photo_attachments.append(attachment)

                if photo_attachments:
                    attachments = ','.join(photo_attachments)
                    send_message(user_id, msg_three, attachments=attachments)

            if text == 'следующий':
                if find_prompt(str(user_id)):
                    params = get_prompt()
                else:
                    msg = 'Ну давай'
                    send_message(user_id, msg)
                    # request_search_parameters(user_id, send_message)
                    params = request_search_parameters(user_id, send_message)

                candidates = find_candidates(user_session, gender=params['gender'], city=params['city'], age=params['age'])
                for person in candidates:
                    send_message(user_id, f'{person["name"]}  https://vk.com/id{person["user_id"]}')
                    photo_attachments = []
                    for photo in person["photos"]:
                        attachment = f"photo{photo['owner_id']}_{photo['id']}"
                        photo_attachments.append(attachment)

                    if photo_attachments:
                        attachments = ','.join(photo_attachments)
                        send_message(user_id, "вот фотки", attachments=attachments)


if __name__ == '__main__':
    # db_reboot.drop_all()
    main()
