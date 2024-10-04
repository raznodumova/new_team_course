import configparser

from sqlalchemy import create_engine, Column, Text, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, relationship
config = configparser.ConfigParser()
config.read('config.ini')

Base = declarative_base()
engine = create_engine(config["DB"]["engine"])


def create_tables():
    return Base.metadata.create_all(engine)


def drop_all():
    return Base.metadata.drop_all(engine)


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, default=" ")
    city = Column(Text, nullable=False, default="Анк-Морпорк")
    gender = Column(Text, nullable=False, default="Не указан")
    age = Column(Integer, nullable=False, default=0)

    prompts = relationship("UserPrompt", backref="user", cascade="all, delete")
    ban = relationship("Banned", backref="user", cascade="all, delete")
    like = relationship("Liked", backref="user", cascade="all, delete")


class UserPrompt(Base):
    __tablename__ = "user_prompt"

    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False, primary_key=True)
    city_for_search = Column(Text, nullable=False, default="Анк-Морпорк")
    gender_for_search = Column(Integer, nullable=False, default=0)
    age_for_search = Column(Integer, nullable=False, default=0)
    offset = Column(Integer, nullable=False, default=0)

class Liked(Base):
    __tablename__ = "liked"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True, nullable=False)
    liked_user_id = Column(Text, primary_key=True, nullable=False)
    name = Column(Text)
    photo = Column(Text)

    PrimaryKeyConstraint("user_id", "liked_user_id", name="uq_like")


class Banned(Base):
    __tablename__ = "banned"

    user_id = Column(Integer, ForeignKey("user.user_id"), primary_key=True, nullable=False)
    banned_user_id = Column(Text, primary_key=True, nullable=False)

    PrimaryKeyConstraint("user_id", "banned_user_id", name="uq_ban")


if __name__ == "__main__":
    pass
