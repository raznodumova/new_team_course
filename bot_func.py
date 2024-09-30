import configparser
from datetime import datetime, date
from random import getrandbits
import db_functions
import db_tables
from keyboard import *
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

config = configparser.ConfigParser()
config.read('config.ini')


class BotFunc:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user_session = vk_api.VkApi(token=config['VK']['user_token']).get_api()
        self.group_session = vk_api.VkApi(token=config['VK']['group_token']).get_api()
        self.longpoll = VkLongPoll(self.group_session)
        self.candidates = self.find_candidates()
        self.counter = 0

    def send_message(self, message, keyb=keyb_for_start, attachments=None):
        self.group_session.messages.send(user_id=self.user_id,
                                         message=message,
                                         keyboard=keyb,
                                         random_id=getrandbits(64),
                                         attachment=attachments)

    def wait_for_response(self) -> str:
        """Функция для ожидания ответа от пользователя."""
        print(f"Ожидание ответа от пользователя {self.user_id}...")
        while True:
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == self.user_id:
                    return event.text

    def get_user_info(self) -> tuple:
        user_info = self.user_session.users.get(user_ids=self.user_id, fields='sex, city, bdate')[0]
        name = user_info.get('first_name', '') + ' ' + user_info.get('last_name', '')
        city = user_info.get('city', {}).get('title', 'Не указан')
        gender = user_info.get('sex', 0)
        try:
            bdate = user_info.get('bdate', '')
            if bdate:
                now_date = date.today()
                age = now_date.year - datetime.strptime(bdate, '%d.%m.%Y').year
            else:
                age = 0
        except Exception as e:
            print(e)
            age = 0

        return name, city, age, gender

    def get_photos(self, user_id) -> str:
        photos = self.user_session.photos.get(owner_id=user_id,
                                              album_id="profile",
                                              count=100,
                                              extended=1,
                                              v=5.199)
        if 'items' not in photos or not photos['items']:
            return "Фото нет"
        else:
            photo_attachments = []
            sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
            top_photos = sorted_photos[:3]
            for photo_ in top_photos:
                max_size = max(photo_['sizes'], key=lambda size: size['width'] * size['height'])
                attachment = f"photo{max_size['owner_id']}_{max_size['id']}"
                photo_attachments.append(attachment)
            attachments = ','.join(photo_attachments)
        return attachments

    def find_candidates(self) -> list:
        prompt_params = self.prompt_create()
        search_results = self.user_session.users.search(sex=prompt_params["gender"],
                                                        age_from=prompt_params["age"] - 2,
                                                        age_to=prompt_params["age"] + 2,
                                                        hometown=prompt_params["city"],
                                                        count=10)  # количество кандидатов для поиска
        candidates_list = []
        for user in search_results['items']:
            candidate_id = user['id']
            photos = self.get_photos(candidate_id)

            candidates_list.append({
                'user_id': user['id'],
                'name': user['first_name'] + ' ' + user['last_name'],
                'photos': photos
            })
        return candidates_list

    def from_01_to_text(self, int_) -> str:
        if int_ == 1:
            return 'женский'
        elif int_ == 2:
            return 'мужской'
        else:
            return 'Не указан'

    def request_search_parameters(self) -> dict:
        # Создаем словарь для хранения параметров поиска
        params = {}

        # Запрашиваем пол
        self.send_message("С кем вам хотелось бы познакомиться", keyb_gender_choise)
        response = None
        while response.lower() not in ['с парнем', 'с девушкой']:
            self.send_message("Я пока не знаю других словов'.", keyb_gender_choise)
            response = self.wait_for_response().lower()
            if response == 'с парнем':
                params['gender'] = 2
            elif response == 'с девушкой':
                params['gender'] = 1

        # запрашиваем возраст
        self.send_message("Введи возраст предполагаемой второй половинки", keyb_for_start)
        age_response = self.wait_for_response()
        # Проверяем, является ли ответ числом
        while not age_response.isdigit() or int(response) < 16:
            self.send_message("Введи возраст нормально, ну, не дурачок же", keyb_for_start)
            age_response = self.wait_for_response()

        params['age'] = age_response

        # Запрашиваем город
        self.send_message("В каком городе ищем? я пока только эти знаю", keyb_for_city)
        response = self.wait_for_response()
        # Сохраняем информацию о городе
        params['city'] = response.strip()

        # Возвращаем собранные параметры
        # print(params)
        prompt = db_tables.UserPrompt(user_id=self.user_id,
                                      city_for_search=params["city"],
                                      gender_for_search=params["gender"],
                                      age_for_search=params["age"])
        db_functions.add_prompt(prompt)
        return params

    def prompt_create(self) -> dict:
        if db_functions.is_prompt_exist(self.user_id) is False:
            self.send_message('Заполним анкету?', keyb=None)
            self.request_search_parameters()
        params = db_functions.get_prompt(self.user_id)
        self.send_message("Ищу...", keyb_for_start)
        return params

    def first_visit(self):
        msg = 'Привет! Рады видеть. Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
        self.send_message(msg, keyb=keyb_for_start)

    def user_profile(self):
        if db_functions.is_user_exist(self.user_id) is False:
            main_user = self.get_user_info()
            user = db_tables.User(user_id=self.user_id,
                                  name=main_user[0],
                                  city=main_user[1],
                                  age=main_user[2],
                                  gender=int(main_user[3]))
            db_functions.create_user(user)
        user_inf = db_functions.get_user_inf_from_db(self.user_id)
        msg_two = (f'Тебя зовут: {user_inf["name"]}\n'
                   f'Ты из: {user_inf["city"]}\n'
                   f'Твой возраст: {user_inf["age"]} лет\n'
                   f'Твой пол: {self.from_01_to_text(user_inf["gender"])}')
        self.send_message(msg_two, keyb_for_start)
        msg_three = 'Вот твои самые классные фотки'
        self.send_message(message=msg_three, keyb=None, attachments=self.get_photos(self.user_id))

    def change_user_inf(self):
        self.send_message("я пока такого не знаю", keyb_for_start)

    def change_user_prompt(self):
        self.send_message("я пока такого не знаю", keyb_for_start)

    def next_(self):
        person = self.candidates[self.counter]
        msg = f'{person["name"]}  https://vk.com/id{person["user_id"]}'
        attachments = person["photos"]
        self.send_message(message=msg, attachments=attachments)
        self.counter += 1
