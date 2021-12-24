import os
import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker, relationship
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from auth.auth import auth_db
from datetime import date, datetime
from typing import Optional, Union
from database_info import sex_info, relation_info


def decor_error(path):
    def _decor_error(old_function):
        def new_function(*args, **kwargs):
            try:
                result = old_function(*args, **kwargs)
            except Exception as error_info:
                print(error_info)
                directory = path.split('/', 1)[0]
                if not os.path.isdir(directory):
                    os.mkdir(directory)
                with open(path, 'a', encoding='utf-8', ) as f:
                    result = None
                    info_list = [str(datetime.now()), old_function.__name__, str(args), str(kwargs),
                                 error_info.__str__()]
                    print(info_list)
                    info = '\n'.join(info_list) + '\n' * 2
                    f.write(info)
            return result
        return new_function
    return _decor_error


Base = declarative_base()


class People(Base):
    __tablename__ = 'people'
    id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String)
    last_name = sq.Column(sq.String)
    sex_id = sq.Column(sq.Integer, sq.ForeignKey('sex.id'))
    date_of_birth = sq.Column(sq.Date)
    city_id = sq.Column(sq.Integer, sq.ForeignKey('city.id'))
    relation_id = sq.Column(sq.Integer, sq.ForeignKey('relation.id'))
    interests = sq.Column(sq.String)
    music = sq.Column(sq.String)
    movies = sq.Column(sq.String)
    tv = sq.Column(sq.String)
    books = sq.Column(sq.String)
    date_of_change = sq.Column(sq.Date, default=date.today(), onupdate=date.today())
    search_parameters = relationship('SearchParameters', secondary='people_search_parameters',
                                     backref='people', uselist=False)


class Sex(Base):
    __tablename__ = 'sex'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String, nullable=False, unique=True)
    peoples = relationship(People, backref='sex')


class City(Base):
    __tablename__ = 'city'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String)
    country_id = sq.Column(sq.Integer, sq.ForeignKey('country.id'))
    peoples = relationship(People, backref='city')


class Country(Base):
    __tablename__ = 'country'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String)
    cities = relationship(City, backref='country')


class Relation(Base):
    __tablename__ = 'relation'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String, nullable=False, unique=True)
    peoples = relationship(People, backref='relation')


class SearchParameters(Base):
    __tablename__ = 'search_parameters'
    id = sq.Column(sq.Integer, sq.ForeignKey('people.id'), primary_key=True)
    city_title = sq.Column(sq.String)
    country_title = sq.Column(sq.String)
    sex_id = sq.Column(sq.Integer, sq.ForeignKey('sex.id'))
    age_from = sq.Column(sq.Integer)
    age_to = sq.Column(sq.Integer)
    relations_id = sq.Column(sq.String)
    interest = sq.Column(sq.String)
    music = sq.Column(sq.String)
    movie = sq.Column(sq.String)
    tv = sq.Column(sq.String)
    book = sq.Column(sq.String)
    date_of_change = sq.Column(sq.Date, default=date.today(), onupdate=date.today())
    search_of_vk = sq.Column(sq.Boolean, default=False, onupdate=False)
    sexes = relationship('Sex')


class PeopleSearchParameters(Base):
    __tablename__ = 'people_search_parameters'
    user_id = sq.Column(sq.Integer, sq.ForeignKey('search_parameters.id'), primary_key=True)
    people_id = sq.Column(sq.Integer, sq.ForeignKey('people.id'), primary_key=True)
    blacklist = sq.Column(sq.Boolean, default=False)


class VKinderBase:
    def __init__(self, user: str, password: str, database: str):
        self.user = user
        self.password = password
        self.database = database
        self.DSN = f"postgresql://{self.user}:{self.password}@localhost:5432/{self.database}"
        self.engine = sq.create_engine(self.DSN)
        self.session_db = sessionmaker(bind=self.engine)

    @decor_error('error/database.log')
    def add_a_record_to_a_table(self, table: Base, **kwargs):
        session_ = Session(self.engine)
        record = table(**kwargs)
        session_.add(record)
        try:
            session_.commit()
            return True
        except SQLAlchemyError as error_info:
            print(error_info.args)
            return False

    @decor_error('error/database.log')
    def get_or_edit_a_record_from_a_table(self, table: Base, id_: Union[int, list], edit=False, **kwargs):
        session_ = Session(self.engine)
        result = session_.query(table).get(id_)
        if not result:
            return result
        elif edit:
            for key, value in kwargs.items():
                setattr(result, key, value)
            session_.add(result)
            try:
                session_.commit()
                return True
            except SQLAlchemyError as error_info:
                print(error_info.args)
                return False
        return result

    def add_peoples_to_a_tables(self, info: dict) -> None:
        """Метод добавляет или изменяет данные в таблицу: People;
        и добавляет данныеб если их нет, в таблицы:'Country, City, Relation, Sex.
        info = {'people': {id: {'id': , first_name': ,'last_name': ,'sex_id':  ,'dbirth': ,'city_id': ,'relation_id': ,
                                 'interest': ,'music': ,'movies': ,'tv': ,'books': }, ...},
                'country': {id: {'id': ,'title': }, ...},
                'city': {id: {'id': ,'title': }, ...},
                'relation': {id: {'id': ,'title': }, ...}
                'sex': {id: {'id': ,'title': }, ...}
                }"""
        session_ = Session(self.engine)
        list_people_id = [x[0] for x in session_.query(People.id).all()]
        list_city_id = [x[0] for x in session_.query(City.id).all()]
        list_country_id = [x[0] for x in session_.query(Country.id).all()]
        for key, value in info['country'].items():
            if key not in list_country_id:
                result = Country(**value)
                session_.add(result)
                print(f'Странна "{value}", добавлена в базу')
        for key, value in info['city'].items():
            if key not in list_city_id:
                result = City(**value)
                session_.add(result)
                print(f'Город "{value}", добавлен в базу')
        for key, value in info['people'].items():
            if key in list_people_id:
                result = session_.query(People).get(key)
                for k, v in value.items():
                    setattr(result, k, v)
                session_.add(result)
                print(f'Данные о человеке:"id{value}", изменены в базе')
            else:
                result = People(**value)
                session_.add(result)
                print(f'Человек:"{value}", добавлен в базу')
        session_.commit()

    @decor_error('error/database.log')
    def request_peoples_id_db(self, user_id: int, sex_id: Optional[int] = None, relations_id: Optional[str] = None,
                              city_title: Optional[str] = None, country_title: Optional[str] = None,
                              b_date_from: Optional[date] = None, b_date_to: date = date.today(),
                              interest: Optional[str] = None, music: Optional[str] = None, movie: Optional[str] = None,
                              tv: Optional[str] = None, book: Optional[str] = None, blacklist: Optional[bool] = None
                              ) -> list:
        filter_list = []
        session_ = Session(self.engine)
        if sex_id:
            filter_list.append(f"people.sex_id = {sex_id}")
        if b_date_from:
            filter_list.append(f"people.date_of_birth >= '{b_date_from}'")
        filter_list.append(f"people.date_of_birth < '{b_date_to}'")
        if city_title:
            filter_list.append(f"city.title iLIKE '{city_title}'")
        if country_title:
            filter_list.append(f"country.title iLIKE '{country_title}'")
        if interest:
            filter_list.append(f"people.interests iLIKE '%{interest}%'")
        if music:
            filter_list.append(f"people.music iLIKE '%{music}%'")
        if movie:
            filter_list.append(f"people.movie iLIKE '%{movie}%'")
        if tv:
            filter_list.append(f"people.tv iLIKE '%{tv}%'")
        if book:
            filter_list.append(f"people.book iLIKE '%{book}%'")
        if relations_id:
            filter_list.append(f"people.relation_id in ({relations_id})")
        if blacklist:
            filter_list.append(f"people_search_parameters.user_id = {user_id}"
                               f" AND people_search_parameters.blacklist = true")
        elif blacklist is False:
            filter_list.append(f"people_search_parameters.user_id = {user_id}"
                               f" AND people_search_parameters.blacklist = false")
        else:
            nested_request = f'SELECT people.id AS people_id ' \
                f'FROM people JOIN people_search_parameters ON people.id = people_search_parameters.people_id ' \
                f'WHERE people_search_parameters.user_id = {user_id} AND people_search_parameters.blacklist = true'
            filter_list.append(f'people.id not in ({nested_request})')
        result = session_.query(People.__table__, PeopleSearchParameters.blacklist, City.title.label('city_title')).\
            outerjoin(City).outerjoin(Country).outerjoin(PeopleSearchParameters).\
            filter(text(' AND '.join(filter_list)))
        return result.all()

    def fill_in_the_table(self, table: Base, records: list):
        """С помощьу этого метода заполняем таблицу 'table' из списка 'records'"""
        session_ = Session(self.engine)
        for kwargs in records:
            record = table(**kwargs)
            session_.add(record)
        session_.commit()


if __name__ == '__main__':
    v_kinder_base = VKinderBase(user=auth_db['user'], password=auth_db['password'], database=auth_db['database'])
    Base.metadata.drop_all(v_kinder_base.engine)
    Base.metadata.create_all(v_kinder_base.engine)
    v_kinder_base.fill_in_the_table(Sex, sex_info)
    v_kinder_base.fill_in_the_table(Relation, relation_info)
