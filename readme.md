# Чат-бот для знакомств в VK - "**OXAЁ**"

**ОХАЁ** — учебный проект для поиска людей по определенным параметрам.

## Описание проекта

Данный бот предлагает варианты других пользователей VK, подходящих под параметры:
- Возраст
- Пол
- Город

### Реализованный функционал

- Регистрация пользователя.
- Сбор параметров для поиска.
- Поиск и выдача кандидатов.
- добавление кандидата в список избранных
- добавление кандидата в Бан лист

### Готовящийся к реализации функционал
- Получение токена в автоматическом режиме
- Добавление Лайков/Комментариев под фотографии понравившегося пользователя
- Добавление различных интересов в критерии поиска
- Изменение системы "жесткого" поиска, на систему рекомандаций на основе соотвествия критериям
- Добаление отслеживания пользователя, для более удобной работы с ботом
- Добавление рекламы между каждым меню (шутка)

## Используемые технологии

-**Python**
-**SQL ALCHEMY ORM** - для взаимодействия с БД.
-**PostgreSQL** — Для хранения информации о пользователях.
-**VK_API** — Библиотека для работы с VK.


## Установка и настройка

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/
    ```

2. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

3. Настройте базу данных PostgreSQL при помощи команд в файле db/db_reboot.py

4. в файле config.ini задайте параметры user_token, group_token, DB(url для движка)

5. Запустите бота:

## Архитектура проекта

- **main.py** — основной файл, в котором реализована логика работы бота.
- **bot_func.py** — файл c основными функциями работы бота .
- **phrase_dict.py** — словарь с возможными сообщениями пользователя, как замена if/else конструкции
- **keyboard.py** — кнопки для упрощения взаимодействия с ботом
- **db_func** — функции для взаимодейсвия с БД.
