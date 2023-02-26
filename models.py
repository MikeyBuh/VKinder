import sqlalchemy as sq
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True)
    viewed_users = sq.Column(sq.Integer)
    first_name = sq.Column(sq.String(length=80), nullable=False)
    last_name = sq.Column(sq.String(length=80), nullable=False)
    user_link = sq.Column(sq.String(length=40), nullable=False)

    def __str__(self):
        return f'User {self.id}: {self.user_id}, {self.city}, {self.viewed_users}' \
               f'{self.first_name}, {self.last_name}, {self.user_link}'


def create_tables(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
