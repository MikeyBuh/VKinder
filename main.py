import datetime
import time
import bot
import requests
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables, User, Photo
from config import group_token, user_token, host, user, password, db_name, port

DSN = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

vk_session = vk_api.VkApi(token=group_token)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
print('Bot was created')


def write_msg(user_id, message, keyboard=None):
    post = {'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7)}
    if keyboard is not None:
        post['keyboard'] = keyboard.get_keyboard()
    else:
        post = post
    vk_session.method('messages.send', post)


def get_user_sex(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': group_token,
              'user_ids': user_id,
              'fields': 'sex',
              'v': '5.131'}
    resp = requests.get(url, params=params)
    response = resp.json()
    for j in response['response']:
        if j.get('sex') == 1:
            sex = 2
            return sex
        elif j.get('sex') == 2:
            sex = 1
            return sex


def get_cities(user_id, city_name):
    url = f'https://api.vk.com/method/database.getCities'
    params = {'access_token': user_token,
              'country_id': 1,
              'q': f'{city_name}',
              'need_all': 0,
              'count': 1000,
              'v': '5.131'}
    resp = requests.get(url, params=params)
    response = resp.json()
    for j in response['response']['items']:
        found_city = j.get('title')
        if found_city == city_name:
            found_city_id = j.get('id')
            return int(found_city_id)


def get_user_city(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': group_token,
              'user_ids': user_id,
              'fields': 'city',
              'v': '5.131'}
    resp = requests.get(url, params=params)
    response = resp.json()
    for j in response['response']:
        if 'city' in j:
            city = j.get('city')
            user_city_id = str(city['id'])
            return user_city_id
        elif 'city' not in j:
            write_msg(user_id, 'Enter your city name and tap Search then, please:')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    city_name = event.text.capitalize()
                    user_city_id = get_cities(user_id, city_name)
                    if city_name != '' or city_name is not None:
                        return str(user_city_id)


def get_user_age(user_id):
    url = f'https://api.vk.com/method/users.get'
    params = {'access_token': group_token,
              'user_ids': user_id,
              'fields': 'bdate',
              'v': '5.131'}
    resp = requests.get(url, params=params)
    response = resp.json()
    date_list = response['response']
    for j in date_list:
        if 'bdate' not in j or 'bdate' == None:
            write_msg(user_id, 'Enter you age and tap Search then, please:')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    try:
                        age = event.text
                        while True:
                            if 18 <= int(age) <= 100:
                                year_now = int(datetime.date.today().year)
                                birth_year = year_now - int(age)
                                return birth_year
                            else:
                                write_msg(user_id, f"You stated your real age, didn't you? Repeat, please:")
                                break
                    except ValueError:
                        write_msg(user_id, 'Please enter a valid value, ok?')
                        write_msg(user_id, 'Enter you age and tap Search then, please:')
        try:
            if 'bdate' in j:
                date = j.get('bdate')
                birth_year = int(date.split('.')[2])
                return birth_year
        except IndexError:
            write_msg(user_id, 'Enter you age and tap Search then, please:')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    try:
                        age = event.text
                        while True:
                            if 18 <= int(age) <= 100:
                                year_now = int(datetime.date.today().year)
                                birth_year = year_now - int(age)
                                return birth_year
                            else:
                                write_msg(user_id, f"You stated your real age, didn't you? Repeat, please:")
                                break
                    except ValueError:
                        write_msg(user_id, 'Please enter a valid value, ok?')
                        write_msg(user_id, 'Enter you age and tap Search then, please:')


def find_users(user_id, sex, user_city_id, birth_year):
    count = 1000
    offset = 0
    while offset < 1000:
        response = requests.get('https://api.vk.com/method/users.search',
                                params={'access_token': user_token,
                                        'user_ids': user_id,
                                        'has_photo': 1,
                                        'sex': sex,
                                        'city_id': user_city_id,
                                        'birth_year': birth_year,
                                        'status': '1' or '6',
                                        'offset': offset,
                                        'count': count,
                                        'fields': 'has_photo, sex, city, status',
                                        'v': '5.131'})
        offset += count
        time.sleep(0.1)
        try:
            for item in response.json()['response']['items']:
                if 'city' in item and item['is_closed'] is False:
                    city = item.get('city')
                    user_city = city['id']
                    if user_city == int(user_city_id):
                        user = User(user_id=(item['id']),
                                    city=(item['city']['id']),
                                    full_name=f"{item['first_name']} {item['last_name']}",
                                    user_link=('https://vk.com/id' + str(item['id'])))
                        session.add(user)
                        session.commit()
                        session.close()
        except KeyError as error:
            write_msg(user_id, 'You did not enter a valid city name')
            write_msg(user_id, 'Please enter start to initialize search once again')
            return error
    print('Database was created')


def get_photos(user_id, owner_id):
    session.query(User).filter(User.user_id == str(owner_id)).update({"viewed_users": 'Yes'},
                                                                     synchronize_session='fetch')
    session.commit()
    session.close()
    count = 200
    offset = 0
    while offset < 200:
        response = requests.get('https://api.vk.com/method/photos.getAll',
                                params={'access_token': user_token,
                                        'type': 'album',
                                        'owner_id': owner_id,
                                        'extended': 1,
                                        'offset': offset,
                                        'count': count,
                                        'v': '5.131'})
        offset += count
        time.sleep(0.1)
        try:
            for i in response.json()['response']['items']:
                photo_id = i['id']
                response = requests.get('https://api.vk.com/method/photos.get',
                                        params={'access_token': user_token,
                                                'owner_id': owner_id,
                                                'album_id': 'profile',
                                                'photo_ids': photo_id,
                                                'extended': 1,
                                                'v': '5.131'})
                time.sleep(0.1)
                for item in response.json()['response']['items']:
                    photo = Photo(photo_id=(item['id']),
                                  album_id=(item['album_id']),
                                  likes=(item['likes']['count']),
                                  comments=(item['comments']['count']),
                                  photo_link=(item['sizes'][-1]['url']),
                                  id_user=(item['owner_id']))
                    session.add(photo)
                    session.commit()
                    session.close()
        except vk_api.ApiError as error:
            return error
