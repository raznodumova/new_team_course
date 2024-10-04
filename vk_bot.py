from bot_func import VkBotEventType
import configparser
from phrase_dict import phrase_dict
from bot_func import BotFunc, longpoll, group_session
from keyboard import keyb_for_start
from random import getrandbits

config = configparser.ConfigParser()
config.read('config.ini')

def main():
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            user_id = event.obj["message"]["from_id"]
            text = str(event.obj["message"]["text"])
            print(text)
            print(user_id)
            try:
                new_user = BotFunc(user_id)
                phrase_dict.get(text.lower())(new_user, user_id)

            except Exception as e:  # если что то пошло не по плану предалагаем начать с начала
                print(e)
                print("не понятное сообщение")
                group_session.get_api().messages.send(user_id=user_id,
                                                      message="Я вас не понял. Повторите пожалуйста",
                                                      keyboard=keyb_for_start.get_keyboard(),
                                                      inline=False,
                                                      random_id=getrandbits(64),
                                                      attachment=None)


if __name__ == '__main__':
    main()
