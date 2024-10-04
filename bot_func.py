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
            if len(candidates.get(f"{uid}")) < 2:  # если список заканчивается, мы наполняем его и продолжаем листать
                print(candidates)  # можно допилить асинхронность сюда, и наполнять список "бесшовно"
                self.send_message(message="ищу, кто вам подходит лучше всего?", keyb=keyb_go.get_keyboard())
                self.search()
                self.next_(uid)
            else:
                person = candidates.get(f"{uid}").pop(0)  # тут мы пропускаем кандидата если он в бане
                if db_functions.is_banned_inDB(uid=uid, id_for_check=person["user_id"]) is False:
                    db_functions.increase_offset_in_db(
                        db_functions.get_prompt(uid)["offset"] + 1)  # увеличиваем смещение поиска
                    msg = f'{person["name"]}  https://vk.com/id{person["user_id"]}'
                    attachments = person["photos"]
                    self.send_message(message=msg, keyb=keyb_for_search.get_keyboard(), attachments=attachments)
                else:
                    print("пропустили забаненного")
                    db_functions.increase_offset_in_db(db_functions.get_prompt(uid)["offset"] + 1)
                    self.next_(uid)
        except Exception as e:
            print(e)
            # self.send_message(message="приступим?", keyb=keyb_go.get_keyboard())
            self.search()
            self.next_(uid)
            # self.wait_for_response()

    def change_user_inf(self, *args):
        self.send_message("я пока не знаю этой команды", keyb_user_profile.get_keyboard())

    def change_user_prompt(self, *args):
        self.send_message("я пока не знаю этой команды", keyb_user_profile.get_keyboard())

    def first_visit(self, uid):
        msg = 'Привет! Рады видеть. Мы придумали для тебя кнопочки, чтоб нам было проще друг друга понимать'
        self.send_message(msg, keyb=keyb_for_start.get_keyboard())

    def from_01_to_text(self, int_) -> str:
        # вк понимает только 1/2
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
        str_photos = " "
        if 'items' not in photos or not photos['items']:      # тут мы запрашиваем фотки, сортируем их по полуярности
            return str_photos
        else:
            sorted_photos = sorted(photos['items'], key=lambda x: x['likes']['count'], reverse=True)
            top_photos = sorted_photos[:3]
            max_size_photos = []
            one_more_list_with_photo = []

            for photo in top_photos:   # так же сортируем по размеру
                max_size_photo = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
                max_size_photos.append({
                    'url': max_size_photo['url'],
                    'owner_id': photo['owner_id'],
                    'id': photo['id']
                })
                for max_photo in max_size_photos:  # и делаем манипуляции для удобства использования в будущем
                    some_photo = f"photo{max_photo['owner_id']}_{max_photo['id']}"
                    one_more_list_with_photo.append(some_photo)
                str_photos = ",".join(one_more_list_with_photo)
        return str_photos

    def like(self, uid):
        # добавляем лайкнутого персонажа в БД
        candidate_id = candidates[f"{uid}"][0]["user_id"]
        candidate_name = candidates[f"{uid}"][0]["name"]
        candidate_photo = candidates[f"{uid}"][0]["photos"]
        try:
            db_functions.like(user_id=uid, liked_user_id=candidate_id, name=candidate_name, photo=candidate_photo)
            self.send_message("лайк добавлен", keyb=keyb_for_search.get_keyboard())
        except Exception as e:
            print(e)
            self.send_message("чет не так, лайк не добавлен", keyb=keyb_for_search.get_keyboard())

    def liked_people(self, uid):
        # получаем список избранных из БД
        liked_people = db_functions.get_likes_list(uid)
        self.send_message(f"У вас {len(liked_people)} людей в избранном", keyb=keyb_for_likes.get_keyboard())
        return liked_people

    def see_all_liked_people(self, uid):  # выдаем всех избранных разом
        # надо будет сделать как то по другому, вдруг у человека 500 избранных
        if len(self.liked_people(uid)) < 1:
            self.send_message("вы еще никого не лайкали", keyb=keyb_user_profile.get_keyboard())
        for people in self.liked_people(uid=uid):
            name = f'{people.get("name")}'
            url = f'https://vk.com/id{people.get("user_id")}'
            atach = f'{people.get("photo")}'
            self.send_message(f"{name} {url}", keyb=keyb_user_profile.get_keyboard(), attachments=atach)

    def clear_favor(self, uid):
        favors = db_functions.get_likes_list(uid)
        if len(favors) < 1:
            self.send_message(f"Лайков нет", keyb=keyb_user_profile.get_keyboard())
        else:
            for people in favors:
                user_for_unlike = people.get("id")
                db_functions.unlike(user_id=uid, user_for_unlike=user_for_unlike)
                self.send_message(f"Лайки убраны", keyb=keyb_user_profile.get_keyboard())

    def ban(self, uid):
        candidate_id = candidates[f"{uid}"][0]["user_id"]
        db_functions.ban(user_id=uid, user_for_ban=candidate_id)
        self.send_message("Вы больше не увидите этого человека", keyb=empty_keybord)
        self.next_(uid)
