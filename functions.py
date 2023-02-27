import datetime
import heapq
import operator
import time
import requests
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables
from config import *

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


def get_user_info(user_id):
    url = 'https://api.vk.com/method/users.get'
    params = {'access_token': group_token,
              'user_ids': user_id,
              'fields': 'sex, city, bdate',
              'v': '5.131'}
    resp = requests.get(url, params=params)
    response = resp.json()
    for j in response['response']:
        for key, value in j.items():
            sex = j.get('sex')
            city = j.get('city')
            bdate = j.get('bdate')
            first_name = j.get('first_name')
            return sex, city, bdate, first_name


def get_user_sex(sex):
    if sex[0] == 1:
        sex = 2
        return sex
    elif sex[0] == 2:
        sex = 1
        return sex


def get_cities(user_id, city_name):
    url = 'https://api.vk.com/method/database.getCities'
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


def get_user_city(user_id, city):
    if city[1] is None:
        write_msg(user_id, 'Enter your city name, please:')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                city_name = event.text.capitalize()
                user_city_id = get_cities(user_id, city_name)
                return str(user_city_id)
    elif city is not None:
        user_city_id = str(city[1]['id'])
        return user_city_id


def get_user_age(user_id, bdate):
    if bdate[2] is None:
        write_msg(user_id, 'Enter your age, please:')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                age = event.text
                try:
                    while True:
                        if 18 <= int(age) <= 99:
                            year_now = int(datetime.date.today().year)
                            birth_year = year_now - int(age)
                            return birth_year
                        else:
                            write_msg(user_id, f"You stated your real age, didn't you? Repeat, please:")
                            break
                except ValueError:
                    write_msg(user_id, 'Please enter a valid value, ok?')
                    write_msg(user_id, 'Enter your age, please:')
    elif len(bdate[2]) <= 5:
        write_msg(user_id, 'Enter your age, please:')
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                age = event.text
                try:
                    while True:
                        if 18 <= int(age) <= 99:
                            year_now = int(datetime.date.today().year)
                            birth_year = year_now - int(age)
                            return birth_year
                        else:
                            write_msg(user_id, f"You stated your real age, didn't you? Repeat, please:")
                            break
                except ValueError:
                    write_msg(user_id, 'Please enter a valid value, ok?')
                    write_msg(user_id, 'Enter your age, please:')
    elif bdate is not None:
        birth_year = int(bdate[2].split('.')[2])
        return birth_year


def find_users(user_id, user_city_id, offset):
    count = 100
    response = requests.get('https://api.vk.com/method/users.search',
                            params={'access_token': user_token,
                                    'user_ids': user_id,
                                    'has_photo': 1,
                                    'sex': get_user_sex(sex=get_user_info(user_id)),
                                    'city_id': user_city_id,
                                    'birth_year': get_user_age(user_id, bdate=get_user_info(user_id)),
                                    'status': '1' or '6',
                                    'offset': offset,
                                    'count': count,
                                    'fields': 'has_photo, sex, city, status',
                                    'v': '5.131'})
    time.sleep(0.2)
    try:
        data_list = response.json()['response']['items']
    except KeyError as error:
        write_msg(user_id, 'You did not enter a valid city name')
        write_msg(user_id, 'Tap "Search" button, please')
        return error
    users_list = []
    for item in data_list:
        if 'city' in item and item['is_closed'] is False:
            city = item.get('city')
            user_city = city['id']
            if user_city == int(user_city_id):
                users_list.append(item)
    var = users_list
    print('Search completed')
    write_msg(user_id, f'Search completed! Tap "Go" button, please')
    return var,


def get_photos(user_id, users_id):
    count = 200
    offset = 0
    while offset < 200:
        response = requests.get('https://api.vk.com/method/photos.getAll',
                                params={'access_token': user_token,
                                        'type': 'album',
                                        'owner_id': users_id,
                                        'extended': 1,
                                        'offset': offset,
                                        'count': count,
                                        'v': '5.131'})
        data = response.json()['response']['items']
        offset += count
        time.sleep(0.2)
        photo_id_list = []
        for item in data:
            photo_id_list.append(item['id'])
        response = requests.get('https://api.vk.com/method/photos.get',
                                params={'access_token': user_token,
                                        'owner_id': users_id,
                                        'album_id': 'profile',
                                        'photo_ids': str(photo_id_list),
                                        'extended': 1,
                                        'v': '5.131'})
        data = response.json()['response']['items']
        time.sleep(0.2)
        photos_dict = {}
        for item in data:
            likes = item['likes']['count']
            comments = item['comments']['count']
            url = item['sizes'][-1]['url']
            photos_dict[url] = int(likes), int(comments)
        if len(photos_dict) == 0:
            write_msg(user_id, f'There are no photos here yet')
        else:
            write_msg(user_id, f'Done!')
        top3 = heapq.nlargest(3, photos_dict.items(), key=operator.itemgetter(1))
        for i, j in top3:
            write_msg(user_id, f"Photo: {i}, Likes: {j[0]}, Comments: {j[1]}")
