import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from flask import request, jsonify
from flask.views import MethodView
import app.models as m
from app.validation import validate


load_dotenv()

db_type = os.getenv('DB_TYPE')
login = os.getenv('LOGIN')
password = os.getenv('PASSWORD')
hostname = os.getenv('HOSTNAME')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

DSN = f'{db_type}://{login}:{password}@{hostname}:{db_port}/{db_name}'
engine = sqlalchemy.create_engine(DSN)
Session = sessionmaker(bind=engine)


def create_db():
    if not database_exists(engine.url):
        create_database(engine.url)
    m.create_table(engine)


def get_user(creator_id, session: Session):
    hash_password = validate(request)
    creator_check = session.query(m.Creator).\
        filter(m.Creator.creator_id == creator_id).\
        filter(m.Creator.password == hash_password).first()
    if not creator_check:
        raise {'status': 404,
               'text': 'Пользователь не найден или неверный пароль'}
    creator_info = session.query(m.Creator.creator_name,
                                 m.Creator.creator_email,
                                 m.Advertisement.advertisement_title).\
        join(m.Advertisement, m.Advertisement.creator_id == m.Creator.creator_id).\
        filter(m.Creator.creator_id == creator_id).all()
    if not creator_info:
        creator_info = session.query(m.Creator.creator_name).filter(m.Creator.creator_id == creator_id).all()
        print('b', creator_info)
        creator_info = {'Имя пользователя': creator_info[0][0],
                        'email пользователя': creator_info[0][1],
                        'Объявления пользователя': 'Отсутсвуют'}
    else:
        creator_info = {'Имя пользователя': creator_info[0][0],
                        'email пользователя': creator_info[0][1],
                        'Объявления пользователя': [el[1] for el in creator_info]}
    return {'creator_info': creator_info, 'creator_all': creator_check}


class CreatorView(MethodView):
    def post(self):
        json_data = request.json
        creator_name = json_data['creator_name']
        creator_email = json_data['creator_email']
        hash_password = validate(request)
        with Session() as session:
            creator = m.Creator(creator_name=creator_name, password=hash_password, creator_email=creator_email)
            session.add(creator)
            session.commit()
        return jsonify({'status': 'created'})

    def get(self, creator_id):
        with Session() as session:
            creator_info = get_user(creator_id, session)['creator_info']
        return creator_info

    def patch(self, creator_id):
        json_data = request.json
        with Session() as session:
            get_user(creator_id, session)
            for field, value in json_data.items():
                if field == 'creator_name':
                    session.query(m.Creator).\
                        filter(m.Creator.creator_id == creator_id).\
                        update({'creator_name': value})
                session.commit()
        return jsonify({'status': 'patched'})

    def delete(self, creator_id):
        with Session() as session:
            creator_info = get_user(creator_id, session)['creator_all']
            session.delete(creator_info)
            session.commit()
        return jsonify({'status': 'deleted'})


class AdvertisementsView(MethodView):
    def post(self):
        json_data = request.json
        advertisement_title = json_data['advertisement_title']
        advertisement_description = json_data['advertisement_description']
        creator_id = json_data['creator_id']
        with Session() as session:
            get_user(creator_id, session)
            advertisement = m.Advertisement(advertisement_title=advertisement_title,
                                            advertisement_description=advertisement_description,
                                            creator_id=creator_id)
            session.add(advertisement)
            session.commit()
        return jsonify({'status': 'created'})

    def get(self, advertisement_id):
        with Session() as session:
            advertisement_info = session.query(m.Advertisement.advertisement_title,
                                               m.Advertisement.advertisement_description,
                                               m.Advertisement.advertisement_created_at,
                                               m.Creator.creator_name). \
                join(m.Creator, m.Advertisement.creator_id == m.Creator.creator_id). \
                filter(m.Advertisement.advertisement_id == advertisement_id).first()
        advertisement_dict = {'Заголовок': advertisement_info[0],
                              'Описание': advertisement_info[1],
                              'Время создания': advertisement_info[2],
                              'Автор': advertisement_info[3]
                              }
        return jsonify(advertisement_dict)

    def patch(self, advertisement_id):
        json_data = request.json
        creator_id = json_data['creator_id']
        with Session() as session:
            get_user(creator_id, session)
            for field, value in json_data.items():
                if field == 'advertisement_title':
                    session.query(m.Advertisement).\
                        filter(m.Advertisement.advertisement_id == advertisement_id).\
                        update({'advertisement_title': value})
                elif field == 'advertisement_description':
                    session.query(m.Advertisement).\
                        filter(m.Advertisement.advertisement_id == advertisement_id).\
                        update({'advertisement_description': value})
                elif field == 'advertisement_created_at':
                    session.query(m.Advertisement).\
                        filter(m.Advertisement.advertisement_id == advertisement_id).\
                        update({'advertisement_created_at': value})
                session.commit()
        return jsonify({'status': 'patched'})

    def delete(self, advertisement_id):
        json_data = request.json
        creator_id = json_data['creator_id']
        with Session() as session:
            get_user(creator_id, session)
            try:
                advertisement_info = session.query(m.Advertisement).\
                    filter(m.Advertisement.advertisement_id == advertisement_id).first()
            except:
                raise {'status': 'Объявления не существует'}
            session.delete(advertisement_info)
            session.commit()
        return jsonify({'status': 'deleted'})
