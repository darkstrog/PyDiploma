import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_seen_users_table():
    """СОЗДАНИЕ ТАБЛИЦЫ ПРОСМОТРЕННЫХ ПОЛЬЗОВАТЕЛЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
    print("[INFO] Table SEEN_USERS was created.")


def insert_seen_users(_user_id):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id) VALUES ('{_user_id}');"""
        )


def select_seen_users():
    """ВЫБОРКА ПРОСМОТРЕННЫХ ПОЛЬЗОВАТЕЛЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(f"""SELECT vk_id FROM seen_users""")
        return cursor.fetchall()


def drop_seen_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_users CASCADE;"""
        )
        print('[INFO] Table SEEN_USERS was deleted.')


def create_database():
    # drop_seen_users()
    create_seen_users_table()
