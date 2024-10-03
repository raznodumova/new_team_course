from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm import sessionmaker
from db_tables import engine, User, Liked, UserPrompt, Banned

s = sessionmaker(engine)()

def create_user(user) -> str:
    s.add(user)
    s.commit()
    return "Пользователь Добавлен"

def update_user(user_id, **inf):
    for key, value in inf.items():
        s.query(User).filter(User.user_id.ilike(user_id)).update(inf)
        print(f"строка {key} обновлена. новое значение {value}")
        s.commit()

def delete_user(user_id) -> str:
    try:
        user_to_delete = s.query(User).filter_by(user_id=user_id).first()
        s.delete(user_to_delete)
        s.commit()
        return "Пользователь удален"
    except UnmappedInstanceError:
        return "такой пользователь не существует"

def add_prompt(prompt) -> str:
    try:
        s.add(prompt)
        s.commit()
        return "Запрос добавлен"
    except Exception as e:
        print(e)
        return "Пользователь уже добавил запрос"

def update_prompt(user_id, **inf):
    for key, value in inf.items():
        s.query(UserPrompt).filter(UserPrompt.user_id.ilike(user_id)).update(inf)
        print(f"строка {key} обновлена. новое значение {value}")
        s.commit()

def like(user_id, liked_user_id):
    try:
        s.add(Liked(user_id=user_id, liked_user_id=liked_user_id))
        s.commit()
        print("Лайк добавлен")

    except IntegrityError:
        print("Лайк уже существует")

def unlike(user_id, user_for_unlike):
    s.delete(Liked(user_id=user_id, liked_user_id=user_for_unlike))
    s.commit()
    print("Лайк убран")

def ban(user_id, user_for_ban):
    try:
        s.add(Banned(user_id=user_id, banned_user_id=user_for_ban))
        s.commit()
        print("Бан добавлен")

    except IntegrityError:
        print("Бан уже существует")

def unban(user_id, user_for_unban):
    s.delete(s.query(Banned).filter_by(user_id=user_id, banned_user_id=user_for_unban).first())
    s.commit()
    print("Бан Убран")

def is_prompt_exist(id_for_find) -> bool:
    try:
        assert s.query(UserPrompt).filter_by(user_id=str(id_for_find)).first().user_id
        print("запрос есть")
        return True
    except Exception as e:
        print("поискового запроса нет в бд")
        print(e)
        return False

def get_prompt(user_id) -> dict:
    _ = {}
    obj = s.query(UserPrompt).filter_by(user_id=str(user_id)).one()
    _["user_id"] = obj.user_id
    _["gender"] = obj.gender_for_search
    _["age"] = int(obj.age_for_search)
    _["city"] = obj.city_for_search
    _["offset"] = obj.offset
    return _

def is_user_exist(user_for_check:int) -> bool:
    try:
        assert s.query(User).filter_by(user_id=str(user_for_check)).first()
        print("пользователь есть")
        return True
    except Exception as e:
        print("пользователя нет")
        print(e)
        return False

def get_user_inf_from_db(*args) -> dict:
    obj = s.query(User).filter_by(user_id=str(*args)).one()
    return {
        "user_id": obj.user_id,
        "name": obj.name,
        "age": obj.age,
        "gender": obj.gender,
        "city": obj.city
    }

def increase_offset_in_db(int_):
    _ = s.get(UserPrompt, "458719538")
    _.offset = int_
    s.commit()


if __name__ == "__main__":
    pass
    # print(get_user_inf_from_db("458719538"))
    # print(get_user_inf_from_db(458719538))
    # print(is_prompt_exist(458719538))
    # print(is_user_exist(6))
    # # user = User(user_id=458719538, name="Александр валерьевич", city="москва", age=26, gender=2)
    # # create_user(user)
    # print(is_user_exist(458719538))
    # prompt = UserPrompt(user_id=1, age_for_search=26, city_for_search="москва", gender_for_search=1)
    # add_prompt(prompt)
    # s.commit()
    # print(get_prompt().city_for_search)
    # print(get_prompt().age_for_search)
    # print(get_prompt().gender_for_search)
