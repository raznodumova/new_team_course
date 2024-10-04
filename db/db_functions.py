from sqlalchemy.exc import IntegrityError, PendingRollbackError
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.orm import sessionmaker
from db.db_tables import engine, User, Liked, UserPrompt, Banned

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

def like(user_id, liked_user_id, name, photo):
    try:
        s.add(Liked(user_id=user_id, liked_user_id=liked_user_id, name=name, photo=photo))
        s.commit()
        print("Лайк добавлен")
        return True
    except IntegrityError:
        print("Лайк уже существует")
        return True
    except PendingRollbackError:
        print("Лайк уже существует")
        return True
    except Exception as e:
        print(e)
        return False

def unlike(user_id, user_for_unlike):
    a = s.query(Liked).filter_by(user_id=user_id, liked_user_id=user_for_unlike).first()
    s.delete(a)
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
        assert s.query(UserPrompt).filter_by(user_id=id_for_find).first().user_id
        print("запрос есть")
        return True
    except Exception as e:
        print("поискового запроса нет в бд")
        print(e)
        return False

def get_prompt(user_id) -> dict:
    _ = {}
    obj = s.query(UserPrompt).filter_by(user_id=user_id).one()
    _["user_id"] = obj.user_id
    _["gender"] = obj.gender_for_search
    _["age"] = int(obj.age_for_search)
    _["city"] = obj.city_for_search
    _["offset"] = obj.offset
    return _

def is_user_exist(user_for_check: int) -> bool:
    try:
        assert s.query(User).filter_by(user_id=user_for_check).first()
        print("пользователь есть")
        return True
    except Exception as e:
        print("пользователя нет")
        print(e)
        return False

def get_user_inf_from_db(uid) -> dict:
    obj = s.query(User).filter_by(user_id=uid).one()
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

def get_likes_list(uid):
    likes_list = []
    response = s.query(Liked).filter_by(user_id=uid).all()
    for item in response:
        user = {"id": item.liked_user_id,
                "name": item.name,
                "photo": item.photo}
        likes_list.append(user)
    return likes_list

def is_banned_inDB(uid, id_for_check) -> bool:
    a = s.query(Banned).filter_by(user_id=uid, banned_user_id=id_for_check).all()
    print(a)
    if len(a) > 0:
        return True
    else:
        return False


if __name__ == "__main__":
    pass
    # unlike(458719538, 681331570)
    # ban(458719538, 472579328)
    # print(is_banned_inDB(uid=458719538, id_for_check=472579328))
