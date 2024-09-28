import db_functions
import db_reboot
import db_tables
from bot_func import get_user_photo, get_gender, get_user_city, get_user_age, get_user_name, change_gender, group_token, user_token, wrt_msg
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
import configparser
from keyboard import keyb


config = configparser.ConfigParser()
config.read('config.ini')


def main():
    token1 = group_token()
    user_tok = user_token()
    vk_session = vk_api.VkApi(token=config['VK']['group_token'])
    longpoll = VkLongPoll(vk_session)

    vk = vk_session.get_api()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                user_id = event.user_id
                message = event.text.lower()

                if message == 'начать':
                    msg = 'Привет, братишка! Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
                    wrt_msg(user_id, msg)


if __name__ == '__main__':
    main()





