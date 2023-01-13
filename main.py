import vk_api
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
from database import *


class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=group_token)  # АВТОРИЗАЦИЯ СООБЩЕСТВА
        self.vk_user_session = vk_api.VkApi(token=user_token)
        self.longpoll = VkLongPoll(self.vk_session)  # ПУЛЛ СОБЫТИЙ НА СТОРОНЕ VK
        self.offset = 0 #СМЕЩЕНИЕ ПОИСКА
        self.find_count = 500 #КОЛИЧЕСТВО ИСКОМЫХ ЛЮДЕЙ ЗА ОДИН ЗАПРОС

    """МЕТОД ОТПРАВКИ СООБЩЕНИЙ"""
    def write_msg(self, user_id, message):
        self.vk_session.method('messages.send',
                               {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

    '''ПОЛУЧАЕМ ДАННЫЕ О ПОЛЬЗОВАТЕЛЕ НАПИСАВШЕМ В БОТ'''
    def get_vk_user(self, _user_id):
        vk_user = self.vk_session.method('users.get', {'user_ids': _user_id, 'fields': 'bdate, sex, city, relation'})
        return vk_user[0]

    """ПОЛУЧЕНИЕ ПОЛА ПОЛЬЗОВАТЕЛЯ, МЕНЯЕТ НА ПРОТИВОПОЛОЖНЫЙ"""
    def get_sex(self, _vk_user):
        _vk_user_sex = _vk_user.get("sex")
        if _vk_user_sex == 1:
            return 2
        elif _vk_user_sex == 2:
            return 1

    """ПОЛУЧЕНИЕ ВОЗРАСТА ПОЛЬЗОВАТЕЛЯ ИЛИ НИЖНЕЙ ГРАНИЦЫ ДЛЯ ПОИСКА"""
    def get_age_low(self, _vk_user):
        year_now = int(datetime.date.today().year)
        user_bdate = _vk_user.get("bdate")
        date_list = user_bdate.split('.')
        if len(date_list) == 3:
            year = int(date_list[2])
            return year_now - year
        else:
            age = ''
            while not age.isdigit():
                self.write_msg(_vk_user.get("id"), 'Введите нижний порог возраста (min - 16): ')
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        if age.isdigit():
                            return age

    def get_user_age(self, _vk_user):
        year_now = int(datetime.date.today().year)
        user_bdate = _vk_user.get("bdate")
        date_list = user_bdate.split('.')
        if len(date_list) == 3:
            year = int(date_list[2])
            return year_now - year
        else:
            self.write_msg(_vk_user.get("id"), 'Введите ваш возраст (минимально допустимый - 16): ')
            age = ''
            while not age.isdigit():
                for event in self.longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                        age = event.text
                        if age.isdigit() and int(age) > 15:
                            return age

    def get_age_span(self, _vk_user):
        self.write_msg(_vk_user.get("id"), 'На сколько старше или младше искомый человек: ')
        age_span = ''
        while not age_span.isdigit():
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    age = event.text
                    if age.isdigit():
                        return age
                    else:
                        self.write_msg(_vk_user.get("id"), 'Это должна быть цифра')

    """ПОЛУЧЕНИЕ ID ГОРОДА ПОЛЬЗОВАТЕЛЯ ПО НАЗВАНИЮ"""
    # @staticmethod
    def cities(self, city_name):
        user_city = self.vk_user_session.method('database.getCities',
                                                {'country_id': 1, 'q': f'{city_name}', 'need_all': 0, 'count': 1000})
        return user_city.get("id")

    """ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ГОРОДЕ ПОЛЬЗОВАТЕЛЯ"""
    def find_city(self, _vk_user):
        if "id" in _vk_user.get("city"):
            return _vk_user.get("city").get("id")
        else:
            _user_id = _vk_user.get("id")
            self.write_msg(_user_id, 'Введите название вашего города: ')
            for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city_name = event.text
                    return self.cities(city_name)

    """ПОИСК ЧЕЛОВЕКА ПО ПОЛУЧЕННЫМ ДАННЫМ"""

    def find_persons(self, _vk_user):
        _age_span = self.get_age_span(_vk_user)
        _user_age = self.get_user_age(_vk_user)
        _age_from = int(_user_age) - int(_age_span)
        _age_to = int(_user_age) + int(_age_span)

        _response = self.vk_user_session.method('users.search',
                                                {
                                                    'sex': self.get_sex(_vk_user),
                                                    'age_from': _age_from,
                                                    'age_to': _age_to,
                                                    'city': self.find_city(_vk_user),
                                                    'fields': 'is_closed, id, first_name, last_name',
                                                    'status': '1' or '6',
                                                    'count': self.find_count,
                                                    'offset': self.offset

                                                })
        _found_users = _response.get("items")
        for _user in _found_users:
            if not _user.get("is_closed"):
                first_name = _user.get('first_name')
                last_name = _user.get('last_name')
                vk_id = str(_user.get('id'))
                vk_link = 'vk.com/id' + str(_user.get('id'))
                insert_found_users(vk_id, first_name, last_name, vk_link)
                self.offset += int(self.find_count)
            else:
                continue

    """ПОЛУЧЕНИЕ ID ФОТОГРАФИЙ С РАНЖИРОВАНИЕМ ПО ЛАЙКАМ"""
    def get_photos_id(self, _user_id):
        _response = self.vk_user_session.method('photos.getAll',
                                                {
                                                    'type': 'album',
                                                    'owner_id': _user_id,
                                                    'extended': 1,
                                                    'count': 25
                                                })
        _photos = dict()
        _photos_list = _response.get("items")
        for i in _photos_list:
            photo_id = str(i.get('id'))
            i_likes = i.get('likes')
            if i_likes.get('count'):
                likes = i_likes.get('count')
                _photos[likes] = photo_id
        return sorted(_photos.items(), reverse=True)[0:3]

    """ОТПРАВКА ФОТОГРАФИЙ ПОЛЬЗОВАТЕЛЮ БОТА"""
    def send_photos(self, user_id, _person_id, _photos):
        _attachment = ''
        for p in _photos:
            _attachment += f",photo{_person_id}_{p[1]}"
        self.vk_session.method('messages.send', {'user_id': user_id,
                                                 'message': f"Top фотографий:\n",
                                                 'attachment': _attachment[1:],
                                                 'random_id': 0})

    """ОТПРАВЛЯЕМ СЛЕДУЮЩЕГО НАЙДЕННОГО ПОЛЬЗОВАТЕЛЯ"""
    def get_found_person(self, _vk_user):
        _person = select_user()
        self.write_msg(_vk_user.get("id"), f'{_person[0]} {_person[1]},\n ссылка на страницу - {_person[3]}')
        insert_seen_users(_person[2])
        _photos = self.get_photos_id(_person[2])
        self.send_photos(_vk_user.get("id"), _person[2], _photos)


bot = VkBot()
