from pprint import pprint

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

    current_candidate_index = 0
    candidates = None

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            text = event.text.lower()

            if text == 'начать':
                msg = 'Привет, братишка! Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
                send_message(user_id, msg)
                main_user = get_user_info(vk, user_id)
                user = db_tables.User(user_id=user_id, name=main_user[0], city=main_user[1], age=main_user[2], gender=main_user[3])
                create_user(user)
                s.commit()

                def from_01_to_text():
                    if main_user[3] == 1:
                        gender = 'женский'
                    elif main_user[3] == 2:
                        gender = 'мужской'
                    else:
                        gender = 'Не указан'

                    return gender

                msg_two = (f'Тебя зовут: {main_user[0]}\n'
                           f'Ты из: {main_user[1]}\n'
                           f'Твой возраст: {main_user[2]} \n'
                           f'Твой пол: {from_01_to_text()}')
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

            if text == 'поиск':
                handle_search_command(user_id, user_session, send_message)

            elif text == 'Добавить в Избранное':
                if 0 <= current_candidate_index < len(candidates):
                    candidate_to_like = candidates[current_candidate_index]  # Получаем текущего кандидата
                    fav = Liked(user_id=user_id, liked_id=candidate_to_like["user_id"])  # Создаем запись для избранного
                    like(user_id, candidate_to_like["user_id"])  # Функция, которая добавляет кандидата в избранное
                    print(fav)
                    send_message(user_id,f'Кандидат {candidate_to_like["name"]} добавлен в Избранное!', keyboard=keyb_for_search.get_keyboard())
                else:
                    send_message(user_id, 'Нет доступных кандидатов для добавления в избранное.', keyboard=keyb_for_search.get_keyboard())

if __name__ == '__main__':
    # db_reboot.drop_all()
    main()