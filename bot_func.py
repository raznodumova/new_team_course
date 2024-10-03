import configparser
from datetime import datetime, date
from random import getrandbits
import db_functions
import db_tables
from keyboard import *
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

config = configparser.ConfigParser()
config.read('config.ini')
group_session = vk_api.VkApi(token=config['VK']['group_token'])
longpoll = VkBotLongPoll(group_session, group_id=227461675)
user_session = vk_api.VkApi(token=config['VK']['user_token']).get_api()
group_api = group_session.get_api()
candidates = dict()

class BotFunc:
    def __init__(self, user_id):
        self.uid = user_id
        self.check_acc(user_id)

    def send_message(self, message, keyb=empty_keybord, attachments=None):
        group_api.messages.send(user_id=self.uid,
                                message=message,
                                keyboard=keyb,
                                random_id=getrandbits(64),
                                attachment=attachments)

    def wait_for_response(self) -> str:
        """Функция для ожидания ответа от пользователя."""
        print(f"Ожидание ответа от пользователя {self.uid}...")
        while True:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW and event.obj["message"]["from_id"] == self.uid:
                    return str(event.obj["message"]["text"])

    def check_acc(self, user_id) -> bool:
        """проверяет, создан ли акк. если нет, создает и снова проверяет"""
        for i in range(2):
            try:
                if db_functions.is_user_exist(user_id) is True:
                    print(f"юзер отработал {i} раз")
                    return True
                else:
                    self.create_acc()
                    self.check_acc(self.uid)
            except Exception as e:
                print(e)
                self.create_acc()
                self.check_acc(self.uid)

    def create_acc(self):
        """Создает аккаунт и поисковый запрос"""
        print("акк создался")
        user_info = user_session.users.get(user_ids=self.uid, fields='sex, city, bdate')[0]
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
        user = db_tables.User(user_id=self.uid,
                              name=name,
                              city=city,
                              age=age,
                              gender=gender)
        db_functions.create_user(user)
        self.request_search_parameters()

    def request_search_parameters(self) -> dict:
        # Создаем словарь для хранения параметров поиска
        params = {}

        # Запрашиваем пол
        self.send_message("С кем вам хотелось бы познакомиться", keyb=keyb_gender_choise.get_keyboard())
        response = "None"
        while response.lower() not in ['с парнем', 'с девушкой']:
            self.send_message("Я пока не знаю других словов'.", keyb_gender_choise.get_keyboard())
            response = self.wait_for_response().lower()
            if response == 'с парнем':
                params['gender'] = 2
            elif response == 'с девушкой':
                params['gender'] = 1

        # запрашиваем возраст
        self.send_message("Введи возраст предполагаемой второй половинки", keyb_for_start.get_keyboard())
        age_response = self.wait_for_response()
        # Проверяем, является ли ответ числом
        while not age_response.isdigit() or int(age_response) < 16:
            self.send_message("Введи возраст нормально, ну, не дурачок же", keyb_for_start.get_keyboard())
            age_response = self.wait_for_response()

        params['age'] = int(age_response)

        # Запрашиваем город
        self.send_message("В каком городе ищем? я пока только эти знаю", keyb_for_city.get_keyboard())
        response = self.wait_for_response()
        # Сохраняем информацию о городе
        params['city'] = response.strip()

        # Возвращаем собранные параметры
        # print(params)
        prompt = db_tables.UserPrompt(user_id=self.uid,
                                      city_for_search=params["city"],
                                      gender_for_search=params["gender"],
                                      age_for_search=params["age"])
        db_functions.add_prompt(prompt)
        return params

    def user_inf(self, uid):
        """выводит инфу о пользователе"""
        user_inf = db_functions.get_user_inf_from_db(f"{uid}")
        msg_two = (f'Тебя зовут: {user_inf["name"]}\n'
                   f'Ты из: {user_inf["city"]}\n'
                   f'Твой возраст: {user_inf["age"]} лет\n'
                   f'Твой пол: {self.from_01_to_text(user_inf["gender"])}')
        self.send_message(message=msg_two)
        msg_three = 'Вот твои самые классные фотки'
        self.send_message(message=msg_three, attachments=self.get_photos(uid), keyb=keyb_user_profile.get_keyboard())

    def search(self):
        """тут мы наполняем список кандидатов"""
        prompt_params = db_functions.get_prompt(self.uid)
        search_results = user_session.users.search(sex=prompt_params["gender"],
                                                   age_from=prompt_params["age"] - 2,
                                                   age_to=prompt_params["age"] + 2,
                                                   hometown=prompt_params["city"],
                                                   offset=prompt_params["offset"],
                                                   count=5)  # количество кандидатов для поиска
        candidates_list = []

        for user in search_results['items']:
            candidate_id = user['id']
            photos = self.get_photos(candidate_id)

            candidates_list.append({
                'user_id': user['id'],
                'name': user['first_name'] + ' ' + user['last_name'],
                'photos': photos,
            })
        candidates[f"{self.uid}"] = candidates_list
        print("список пополнился")
        print(candidates)
        return candidates_list

    def next_(self, uid):
        """Тут мы выдаем кандидата по одному и удаяем его из списка"""
        try:
            if len(candidates.get(f"{uid}")) < 2:
                print("отработала длинна списка")
                print(candidates)
                self.search()
                self.send_message(message="нужны еще варианты?", keyb=keyb_go.get_keyboard())
                self.wait_for_response()
        except Exception as e:
            print(e)
            self.send_message(message="приступим?", keyb=keyb_go.get_keyboard())
            self.search()
            print("отработал ексепт")
            self.wait_for_response()

        person = candidates.get(f"{uid}").pop(0)
        db_functions.increase_offset_in_db(db_functions.get_prompt(uid)["offset"] + 1)
        print("офсет увелилился")
        msg = f'{person["name"]}  https://vk.com/id{person["user_id"]}'
        attachments = person["photos"]
        self.send_message(message=msg, keyb=keyb_for_search.get_keyboard(),  attachments=attachments)

    def change_user_inf(self):
        self.send_message("я пока такого не знаю", keyb_for_start.get_keyboard())

    def change_user_prompt(self):
        self.send_message("я пока такого не знаю", keyb_for_start.get_keyboard())

    def first_visit(self, uid):
        msg = 'Привет! Рады видеть. Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
        self.send_message(msg, keyb=keyb_for_start.get_keyboard())

    def from_01_to_text(self, int_) -> str:
        if int(int_) == 1:
            return 'женский'
        elif int(int_) == 2:
            return 'мужской'
        else:
            return 'Не указан'

    def get_photos(self, user_id) -> str:
        photos = user_session.photos.get(owner_id=user_id,
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
            # тут что то сломалось,пока лень разбираться
            # for photo_ in top_photos:
            #     max_size = max(photo_['sizes'], key=lambda size: size['width'] * size['height'])
            #     attachment = f"photo{max_size['owner_id']}_{max_size['id']}"
            #     photo_attachments.append(attachment)
            # attachments = ','.join(top_photos)
        return "фото пока нет"
    # def __init__(self, user_id: int):
    #     self.user_id = user_id

    # def send_message(self, message, keyb=empty_keybord, attachments=None):
    #     group_api.messages.send(user_id=self.user_id,
    #                             message=message,
    #                             keyboard=keyb,
    #                             random_id=getrandbits(64),
    #                             attachment=attachments)
    #
    # def wait_for_response(self) -> str:
    #     """Функция для ожидания ответа от пользователя."""
    #     print(f"Ожидание ответа от пользователя {self.user_id}...")
    #     while True:
    #         for event in longpoll.listen():
    #             if event.type == VkBotEventType.MESSAGE_NEW and event.obj["message"]["from_id"] == self.user_id:
    #                 return str(event.obj["message"]["text"])

    # def get_user_info(self) -> tuple:
    #     user_info = user_session.users.get(user_ids=self.user_id, fields='sex, city, bdate')[0]
    #     name = user_info.get('first_name', '') + ' ' + user_info.get('last_name', '')
    #     city = user_info.get('city', {}).get('title', 'Не указан')
    #     gender = user_info.get('sex', 0)
    #     try:
    #         bdate = user_info.get('bdate', '')
    #         if bdate:
    #             now_date = date.today()
    #             age = now_date.year - datetime.strptime(bdate, '%d.%m.%Y').year
    #         else:
    #             age = 0
    #     except Exception as e:
    #         print(e)
    #         age = 0
    #
    #     return name, city, age, gender

    # def get_photos(self, user_id) -> str:
    #     photos = user_session.photos.get(owner_id=user_id,
    #                                      album_id="profile",
    #                                      count=100,
    #                                      extended=1,
    #                                      v=5.199)
    #     if 'items' not in photos or not photos['items']:
    #         return "Фото нет"
    #     else:
    #         photo_attachments = []
    #         sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
    #         top_photos = sorted_photos[:3]
    #         # тут что то сломалось,пока лень разбираться
    #         # for photo_ in top_photos:
    #         #     max_size = max(photo_['sizes'], key=lambda size: size['width'] * size['height'])
    #         #     attachment = f"photo{max_size['owner_id']}_{max_size['id']}"
    #         #     photo_attachments.append(attachment)
    #         # attachments = ','.join(top_photos)
    #     return "фото пока нет"
    #
    # def find_candidates(self):
        # prompt_params = self.prompt_create()
        # search_results = user_session.users.search(sex=prompt_params["gender"],
        #                                            age_from=prompt_params["age"] - 2,
        #                                            age_to=prompt_params["age"] + 2,
        #                                            hometown=prompt_params["city"],
        #                                            count=10)  # количество кандидатов для поиска
        # candidates_list = []
        #
        # for user in search_results['items']:
        #     candidate_id = user['id']
        #     photos = self.get_photos(candidate_id)
        #
        #     candidates_list.append({
        #         'user_id': user['id'],
        #         'name': user['first_name'] + ' ' + user['last_name'],
        #         'photos': photos
        #     })
        # candidates[f"{self.user_id}"] = candidates_list
        # return  candidates_list

    # def from_01_to_text(self, int_) -> str:
    #     if int(int_) == 1:
    #         return 'женский'
    #     elif int(int_) == 2:
    #         return 'мужской'
    #     else:
    #         return 'Не указан'

    # def request_search_parameters(self) -> dict:
    #     # Создаем словарь для хранения параметров поиска
    #     params = {}
    #
    #     # Запрашиваем пол
    #     self.send_message("С кем вам хотелось бы познакомиться", keyb=keyb_gender_choise.get_keyboard())
    #     response = "None"
    #     while response.lower() not in ['с парнем', 'с девушкой']:
    #         self.send_message("Я пока не знаю других словов'.", keyb_gender_choise.get_keyboard())
    #         response = self.wait_for_response().lower()
    #         if response == 'с парнем':
    #             params['gender'] = 2
    #         elif response == 'с девушкой':
    #             params['gender'] = 1
    #
    #     # запрашиваем возраст
    #     self.send_message("Введи возраст предполагаемой второй половинки", keyb_for_start.get_keyboard())
    #     age_response = self.wait_for_response()
    #     # Проверяем, является ли ответ числом
    #     while not age_response.isdigit() or int(age_response) < 16:
    #         self.send_message("Введи возраст нормально, ну, не дурачок же", keyb_for_start.get_keyboard())
    #         age_response = self.wait_for_response()
    #
    #     params['age'] = int(age_response)
    #
    #     # Запрашиваем город
    #     self.send_message("В каком городе ищем? я пока только эти знаю", keyb_for_city.get_keyboard())
    #     response = self.wait_for_response()
    #     # Сохраняем информацию о городе
    #     params['city'] = response.strip()
    #
    #     # Возвращаем собранные параметры
    #     # print(params)
    #     prompt = db_tables.UserPrompt(user_id=self.user_id,
    #                                   city_for_search=params["city"],
    #                                   gender_for_search=params["gender"],
    #                                   age_for_search=params["age"])
    #     db_functions.add_prompt(prompt)
    #     return params

    # def prompt_create(self) -> dict:
    #     if db_functions.is_prompt_exist(self.user_id) is False:
    #         self.send_message(message='Заполним анкету?')
    #         self.request_search_parameters()
    #     params = db_functions.get_prompt(self.user_id)
    #     self.send_message("Ищу...", keyb_for_start.get_keyboard())
    #     return params

    # def first_visit(self):
    #     msg = 'Привет! Рады видеть. Мы придумали для тебя кнопочки, чтобы тебе было легче оринтироваться'
    #     self.send_message(msg, keyb=keyb_for_start.get_keyboard())

    # def user_profile(self):
    #     # if db_functions.is_user_exist(self.user_id) is False:
    #     #     main_user = self.get_user_info()
    #     #     user = db_tables.User(user_id=self.user_id,
    #     #                           name=main_user[0],
    #     #                           city=main_user[1],
    #     #                           age=main_user[2],
    #     #                           gender=int(main_user[3]))
    #     #     db_functions.create_user(user)
    #     # user_inf = db_functions.get_user_inf_from_db(self.user_id)
    #     # msg_two = (f'Тебя зовут: {user_inf["name"]}\n'
    #     #            f'Ты из: {user_inf["city"]}\n'
    #     #            f'Твой возраст: {user_inf["age"]} лет\n'
    #     #            f'Твой пол: {self.from_01_to_text(user_inf["gender"])}')
    #     # self.send_message(msg_two, keyb_for_start.get_keyboard())
    #     # msg_three = 'Вот твои самые классные фотки'
    #     # self.send_message(message=msg_three, attachments=self.get_photos(self.user_id))
    #     # if self.user_id not in candidates.keys():
    #     #     self.send_message(message="Остался еще один шаг")
    #     #     self.prompt_create()
    #
    # def change_user_inf(self):
    #     self.send_message("я пока такого не знаю", keyb_for_start.get_keyboard())
    #
    # def change_user_prompt(self):
    #     self.send_message("я пока такого не знаю", keyb_for_start.get_keyboard())
    #
    # def next_(self):
    #     person = candidates.get(f"{self.user_id}").pop()
    #     msg = f'{person["name"]}  https://vk.com/id{person["user_id"]}'
    #     attachments = person["photos"]
    #     self.send_message(message=msg, attachments=attachments)
