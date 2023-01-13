import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_found_users_table():
    """СОЗДАНИЕ ТАБЛИЦЫ НАЙДЕННЫХ ПОЛЬЗОВАТЕЛЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS found_users(
                vk_id varchar(20) NOT NULL PRIMARY KEY,
                id serial,
                first_name varchar(50) NOT NULL,
                last_name varchar(30) NOT NULL,
                vk_link varchar(50));"""
        )
    print("[INFO] Table FOUND_USERS was created.")


def create_seen_users_table():
    """СОЗДАНИЕ ТАБЛИЦЫ ПРОСМОТРЕННЫХ ПОЛЬЗОВАТЕЛЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
            id serial,
            vk_id varchar(50) PRIMARY KEY);"""
        )
    print("[INFO] Table SEEN_USERS was created.")


def insert_found_users(vk_id, first_name, last_name, vk_link):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ FOUND_USERS"""
    _first_name = first_name.replace("'", "''")
    _last_name = last_name.replace("'", "''")
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO found_users (vk_id, first_name, last_name, vk_link) 
                VALUES ('{vk_id}', '{_first_name}', '{_last_name}', '{vk_link}');"""
        )


def get_offset():
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT id FROM seen_users ORDER BY id DESC LIMIT 1;"
        )
        return cursor.fetchone()


def insert_seen_users(_user_id):
    """ВСТАВКА ДАННЫХ В ТАБЛИЦУ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id) VALUES ('{_user_id}');"""
        )


def select_user():
    """ВЫБОРКА НЕПРОСМОТРЕННЫХ ПОЛЬЗОВАТЕЛЕЙ"""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT fu.first_name,
                        fu.last_name,
                        fu.vk_id,
                        fu.vk_link,
                        su.vk_id
                        FROM found_users AS fu
                        LEFT JOIN seen_users AS su 
                        ON fu.vk_id = su.vk_id
                        WHERE su.vk_id IS NULL
                        LIMIT '1';"""
        )
        return cursor.fetchone()


def drop_found_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ FOUND_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS found_users CASCADE;"""
        )
        print('[INFO] Table FOUND_USERS was deleted.')


def drop_seen_users():
    """УДАЛЕНИЕ ТАБЛИЦЫ SEEN_USERS"""
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_users CASCADE;"""
        )
        print('[INFO] Table SEEN_USERS was deleted.')


def create_database():
    drop_found_users()
    #drop_seen_users()
    create_found_users_table()
    create_seen_users_table()
