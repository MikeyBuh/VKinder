from functions import *
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from models import User, Base

offset = 0

for event in longpoll.listen():
    global users_list
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        user_id = event.user_id
        if request == 'start':
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            keyboard = VkKeyboard()
            buttons = ['search', 'go', 'exit']
            button_colors = [VkKeyboardColor.NEGATIVE, VkKeyboardColor.PRIMARY, VkKeyboardColor.POSITIVE]
            for btn, btn_color in zip(buttons, button_colors):
                keyboard.add_button(btn, btn_color)
            write_msg(event.user_id, f'Keyboard ready to go!', keyboard)
            first_name = get_user_info(user_id=event.peer_id)
            write_msg(event.user_id, f'Hi, {first_name[3]}! I am a dating bot')
            write_msg(event.user_id, f'Do you need a couple? Tap "Search" button and I will find it for you')
            continue
        elif request == 'search':
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            users_list = find_users(user_id, user_city_id=get_user_city(user_id, city=get_user_info(user_id)), offset=0)
            continue
        elif request == 'go':
            try:
                users = users_list[0][0]
                users_id = users['id']
                write_msg(event.user_id, f'I found a couple for you!')
                write_msg(user_id, f"{(users['first_name'])} {(users['last_name'])}")
                write_msg(user_id, f"User link: {'https://vk.com/id' + str(users['id'])}")
                get_photos(user_id, users_id=users_id)
                user = User(user_id=users['id'], first_name=users['first_name'],
                            last_name=users['last_name'],
                            user_link='https://vk.com/id' + str(users['id']))
                session.add(user)
                session.query(User).filter(User.user_id == str(users['id'])).update({'viewed_users': 1},
                                                                                    synchronize_session='fetch')
                session.commit()
                session.close()
                write_msg(event.user_id, f'Tap "Go" button again if you want to continue')
                users_list[0].remove(users)
                if len(users_list[0]) == 0:
                    offset += 100
                    users_list = find_users(user_id, user_city_id=get_user_city(user_id,
                                            city=get_user_info(user_id)), offset=offset)
            except NameError:
                write_msg(event.user_id, f'You need to search firstly not go! Tap "Search" button, please')
            except TypeError:
                write_msg(event.user_id, f'You need to search firstly not go! Tap "Search" button again, please')
            continue
        elif request == 'exit':
            write_msg(event.user_id, f'Good Luck! You are welcome at any time')
            write_msg(event.user_id, f'Tap "Go" button to continue')
            continue
