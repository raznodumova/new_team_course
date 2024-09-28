from sqlalchemy.exc import IntegrityError
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
        return s.query(UserPrompt).filter_by(user_id=id_for_find).first()
    except Exception as e:
        print(e)
        return None
def get_prompt():
    pass


if __name__ == "__main__":
    pass
