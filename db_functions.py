from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm import sessionmaker
from db_tables import engine, User, Liked, UserPrompt, Banned

s = sessionmaker(engine)()

def create_user(user):
    try:
        s.add(user)
        s.commit()
        print("Пользователь Добавлен")

    except IntegrityError:
        print("Такой пользователь уже существует")

def update_user(user_id, **inf):
    for key, value in inf.items():
        s.query(User).filter(User.user_id.ilike(user_id)).update(inf)
        print(f"строка {key} обновлена. новое значение {value}")
        s.commit()

def delete_user(user_id):
    try:
        user_to_delete = s.query(User).filter_by(user_id=user_id).first()
        s.delete(user_to_delete)
        s.commit()
        print("Пользователь удален")
    except UnmappedInstanceError:
        print("такой пользователь не существует")

def add_prompt(prompt):
    try:
        s.add(prompt)
        s.commit()
        print("Запрос добавлен")

    except IntegrityError:
        print("Пользователь уже добавил запрос")
    except PendingRollbackError:
        print("Пользователь уже добавил запрос")

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

def find_prompt(id_for_find):
    try:
        return s.query(UserPrompt).filter_by(user_id=str(id_for_find)).first().user_id
    except Exception as e:
        print(e)
        return None

def get_prompt(user_id):
    _ = {}
    obj = s.query(UserPrompt).filter_by(user_id=str(user_id)).first()
    _["user_id"] = obj.user_id
    _["gender"] = obj.gender_for_search
    _["age"] = obj.age_for_search
    _["city"] = obj.city_for_search
    return _


if __name__ == "__main__":
    pass
    # user = User(user_id=1, name="Александр валерьевич", city="москва", age=26, gender=2)
    # create_user(user)
    # prompt = UserPrompt(user_id=1, age_for_search=26, city_for_search="москва", gender_for_search=1)
    # add_prompt(prompt)
    # s.commit()
    # print(get_prompt().city_for_search)
    # print(get_prompt().age_for_search)
    # print(get_prompt().gender_for_search)
    if find_prompt(458719538) == str(458719538):
        print("строка")
    elif find_prompt(458719538) == int(458719538):
        print("число")
    else:
        print("хз")