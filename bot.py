from main import *
import psycopg2
from operator import or_
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from models import User, Photo, Base

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        request = event.text.lower()
        age = event.text
        var = event.text
        full_name = var
        owner_id = event.text
        user_id = event.user_id

        if request == 'start':
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            keyboard = VkKeyboard()
            buttons = ['search', 'exit']
            button_colors = [VkKeyboardColor.NEGATIVE, VkKeyboardColor.POSITIVE]
            for btn, btn_color in zip(buttons, button_colors):
                keyboard.add_button(btn, btn_color)
            write_msg(event.user_id, f'Keyboard ready to go!', keyboard)
            user_get = vk.users.get(user_ids=user_id)
            user_get = user_get[0]
            first_name = user_get['first_name']
            write_msg(event.user_id, f'Hi, {first_name}! I am a dating bot')
            write_msg(event.user_id, f'Do you need a couple? Tap Search button and I will find it for you')
            get_user_sex(user_id=event.peer_id)
            find_users(user_id=event.peer_id, sex=get_user_sex(user_id=event.peer_id),
                       user_city_id=get_user_city(user_id=event.peer_id),
                       birth_year=get_user_age(user_id=event.peer_id))
            continue
        elif request == 'search':
            write_msg(event.user_id, f"OK Let's do it")
            write_msg(event.user_id, f'I found a couple for you!')
            for k in session.query(User.full_name, User.user_id, User.user_link).filter(User.viewed_users == None)\
                    .limit(10).all():
                write_msg(event.user_id, '{}, id: {}, link: {}'.format(*k))
            session.commit()
            session.close()
            write_msg(event.user_id, f'What user do you like? I will deliver you its 3 best profile photos'
                                     f'Enter user fullname or id, please:')
            continue
        elif request == 'exit':
            write_msg(event.user_id, f'Good Luck! You are welcome at any time')
            continue
        elif var == full_name:
            try:
                for c in session.query(User.user_id).filter(User.full_name == var).limit(1):
                    owner_id = '{}'.format(*c)
                session.commit()
                write_msg(event.user_id, f'OK')
                write_msg(event.user_id, f'Please wait...')
                get_photos(user_id=event.peer_id, owner_id=owner_id)
                for n in session.query(User.user_link).filter(User.user_id == owner_id).limit(1).all():
                    write_msg(user_id, 'User link: {}'.format(*n))
                for d in session.query(Photo.id, Photo.likes, Photo.comments, Photo.photo_link).join(User) \
                        .filter(or_(User.full_name == var, User.user_id == owner_id))\
                        .order_by(Photo.likes.desc(), Photo.comments.desc()).limit(3).all():
                    write_msg(user_id, 'Photo {}: likes: {}, comments: {}, photo link: {}'.format(*d))
                session.commit()
            except (Exception, psycopg2.Error) as error:
                write_msg(event.user_id, f'Error! Tap Search again or enter user fullname or id correctly, please')
            session.close()
            continue
