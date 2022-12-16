import os

from dotenv import load_dotenv
load_dotenv()

group_token = os.getenv('group_token')
user_token = os.getenv('user_token')
user_token_2 = os.getenv('user_token_2')

host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('password')
db_name = os.getenv('db_name')
port = os.getenv('port')
