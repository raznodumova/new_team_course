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
                if find_prompt(user_id) == str(user_id):
                    params = get_prompt(user_id)
                else:
                    msg = 'Ну давай'
                    send_message(user_id, msg)
                    params = request_search_parameters(user_id, send_message)
                    prompt = UserPrompt(user_id=user_id,
                                        gender_for_search=params['gender'],
                                        city_for_search=params['city'],
                                        age_for_search=params['age'])
                    add_prompt(prompt)

                candidates = find_candidates(user_session, gender=params['gender'], city=params['city'],
                                             age=params['age'])
                msg = ('Чтобы посмотреть следующего кандидата, нажми кнопку "Следующий"\n'
                       'Чтобы добавить кандидата в ЧС, нажми на кнопку "Добавить в ЧС"\n'
                       'Чтобы добавить кандидата в избранное, нажми на кнопку "Добавить в избранное"\n')
                send_message(user_id, msg, keyboard=keyb_for_start.get_keyboard())

                current_candidate_index = 0

                while current_candidate_index < len(candidates):
                    person = candidates[current_candidate_index]  # Получаем текущего кандидата
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

                    if us_msg == 'Следующий':
                        current_candidate_index += 1  # Переход к следующему кандидату
                        print(current_candidate_index)
                        if current_candidate_index >= len(candidates):
                            send_message(user_id, 'Это последний кандидат', keyboard=keyb_for_search.get_keyboard())
                        us_msg = None

                    if us_msg == 'Добавить в Избранное':
                        fav = Liked(user_id=user_id, liked_id=person["user_id"])
                        like(user_id, person["user_id"])
                        print(fav)
                        send_message(user_id, f'Кандидат {person["name"]} добавлен в избранное!', keyboard=keyb_for_search.get_keyboard())


if __name__ == '__main__':
    # db_reboot.drop_all()
    main()