import db_functions
from db_functions import create_user
import db_reboot
import db_tables
from bot_func import wait_for_response, get_user_info, request_search_parameters, get_photos, find_candidates, send_message
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
import configparser
from keyboard import keyb


config = configparser.ConfigParser()
config.read('config.ini')


def main():
    # token_group = 'vk1.a.pt524_volH1KULjGa3epiXZzczIcveDn8AbW0zm8l-91aowhUzuLBg5gVLFrdbnoItfRHm_BEV2YjtwwQlygElRUfAKKSOfcnM9ib7HeUn3Y9P4c3AuMUNIC7YRIMdKy2otm3eeK0jzWdsU9urRPt5I5mXvl4jK0txwdD6PoMllNk4mp8befU3kXMO6CmknhS4WzOxitBxFuyJ45Ik8F3A'
    # user_token = 'vk1.a.uRhJsoETCyrWqItH-cTVEygeNTEM1vxcxD6jZItd8rjSTajCu_UKiuX5bl1JmlnVIzY4uIc7zEchnT1tr9YTugAM4mZPh1pP9dtxVLvU6hsGGHok2q4jROv4a34xkHJ00td0IhySxrB-Jv_q375FXcpz4OH0RH8_v3g0EGKgtFxLVxPg_eAG0W8MOQvroSgp'
    vk_session = vk_api.VkApi(token=config['VK']['group_token'])
    longpoll = VkLongPoll(vk_session)

    user_session = vk_api.VkApi(token=config['VK']['user_token'])

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
                msg = 'Ну давай'
                send_message(user_id, msg)
                request_search_parameters(user_id, send_message)






if __name__ == '__main__':
    # db_reboot.drop_all()
    main()