import requests
# import json
from random import randrange
from vk_api import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import group_token, user_token
from database import *


def main() -> None:
    vk_session = vk_api.VkApi(token=group_token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    print('Bot was created')

    def write_msg(user_id, message):
        vk_session.method('messages.send', {'user_id': user_id,
                                            'message': message,
                                            'random_id': randrange(10 ** 7), })
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            request = event.text.lower()
            user_id = event.user_id

            if request == "hello":
                user_get = vk.users.get(user_ids=user_id)
                user_get = user_get[0]
                first_name = user_get['first_name']
                print(f'Hi!, {first_name}')
                write_msg(event.user_id, f"Hi!, {first_name}")
            elif request == "bye":
                write_msg(event.user_id, "See you next time!")
            else:
                write_msg(event.user_id, "Repeat you message, please")

            def get_name(user_id):
                url = f'https://api.vk.com/method/users.get'
                params = {'access_token': user_token, 'user_ids': user_id, 'v': '5.131'}
                resp = requests.get(url, params=params)
                response = resp.json()
                print(response)
                for j in response['response']:
                    for key in j.keys():
                        first_name = j.get('first_name')
                        return first_name

            get_name(user_id=event.peer_id)

            def get_user_sex(user_id):
                url = f'https://api.vk.com/method/users.get'
                params = {'access_token': group_token, 'user_ids': user_id, 'fields': 'sex', 'v': '5.131'}
                resp = requests.get(url, params=params)
                response = resp.json()
                print(response)
                for j in response['response']:
                    if j.get('sex') == 1:
                        sex = 2
                        return sex
                    elif j.get('sex') == 2:
                        sex = 1
                        return sex
                    # print(j.get('sex'))

            get_user_sex(user_id=event.peer_id)

            def get_user_city(user_id):
                url = f'https://api.vk.com/method/users.get'
                params = {'access_token': group_token, 'user_ids': user_id, 'fields': 'city', 'v': '5.131'}
                resp = requests.get(url, params=params)
                response = resp.json()
                print(response)
                for j in response['response']:
                    for key, value in j.items():
                        city = j.get('city')
                        return city['id']

            get_user_city(user_id=event.peer_id)

            def find_users(user_id, sex, city):

                url = f'https://api.vk.com/method/users.search'
                params = {'access_token': user_token,
                          'user_ids': user_id,
                          'sex': sex,
                          'city': city,
                          'count': 5,
                          'v': '5.131'}
                resp = requests.get(url, params=params)
                response = resp.json()
                print(response)
                with open('users.json', 'w', encoding='utf=8') as file:
                    json.dump(response, file, indent=4, ensure_ascii=False)

            find_users(user_id=event.peer_id, sex=get_user_sex(user_id=event.peer_id),
                       city=get_user_city(user_id=event.peer_id))


if __name__ == '__main__':
    main()
