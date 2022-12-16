import json
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables, Users
from config import host, user, password, db_name, port

DSN = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
engine = sqlalchemy.create_engine(DSN)
create_tables(engine)

Session = sessionmaker(bind=engine)
session = Session()

with open('users.json', 'r') as file:
    data = json.load(file)
    for item in data['response']['items']:
        users = Users(user_id=(item['id']),
                      first_name=(item['first_name']),
                      last_name=(item['last_name'])
                      )
        session.add(users)
        session.commit()
        # print(item['id'])

# session.commit()
session.close()
