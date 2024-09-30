# да ебаный рот этого казино, как блять запушить?
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import configparser
from phrase_dict import phrase_dict
from keyboard import keyb_for_start
from random import getrandbits

config = configparser.ConfigParser()
config.read('config.ini')
group_session = vk_api.VkApi(token=config['VK']['group_token'])
longpoll = VkLongPoll(group_session)

def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_id = event.user_id
            text = event.text
            try:
                phrase_dict.get(text)(user_id)
            except:
                group_session.get_api().messages.send(user_id=user_id,
                                                      message="Я вас не понял. Повторите пожалуйста",
                                                      keyboard=keyb_for_start,
                                                      random_id=getrandbits(64),
                                                      attachment=None)


if __name__ == '__main__':
    main()
