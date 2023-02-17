import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, unique=True)
    city = sq.Column(sq.Integer)
    viewed_users = sq.Column(sq.String(length=40))
    full_name = sq.Column(sq.String(length=80), nullable=False)
    user_link = sq.Column(sq.String(length=40), nullable=False)

    photo = relationship('Photo', backref='user', passive_deletes=True)

    def __str__(self):
        return f'User {self.id}: {self.user_id}, {self.city}, {self.viewed_users}' \
               f'{self.full_name}, {self.user_link}'


class Photo(Base):
    __tablename__ = 'photo'

    id = sq.Column(sq.Integer, primary_key=True)
    photo_id = sq.Column(sq.Integer, unique=True)
    album_id = sq.Column(sq.Integer, nullable=False)
    likes = sq.Column(sq.Integer, nullable=False)
    comments = sq.Column(sq.Integer, nullable=False)
    photo_link = sq.Column(sq.String(length=500), nullable=False)

    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)

    def __str__(self):
        return f'Photo {self.id}: {self.photo_id}, {self.album_id}' \
               f'{self.likes}, {self.comments}, {self.photo_link}'


def create_tables(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
