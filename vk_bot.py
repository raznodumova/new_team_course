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
                handle_start_command(user_id, vk, user_session)

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

                # current_candidate_index = 0

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


            elif text == 'Добавить в Избранное':
                print('CУКА')
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