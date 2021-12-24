import json
import re
import requests
from typing import Optional, Dict
from DataBase import People, SearchParameters, PeopleSearchParameters
from session import v_kinder_base, vk_group, vk_user
from settings import message, message_error
from interface import interface_main, interface_parameters, interface_search_parameters, interface_search_result_photo,\
    interface_button_open_blacklist, interface_change_parameters
from datetime import datetime, date, timedelta
from random import choice

InfoPeoplesDB = Dict[str, Dict[int, dict]]

column_name = {'🏡 город': 'city_title',
               '🌏 страна': 'country_title',
               '👫 пол': 'sex_id',
               '👶 возраст от': 'age_from',
               '🧓 возраст до': 'age_to',
               '👥 статус': 'relations_id',
               '🎨 увлечения': 'interest',
               '🎤 музыка': 'music',
               '🎥 фильмы': 'movie',
               '📺 ТВ': 'tv',
               '📖 книги': 'book'
               }


def user_verification(user_id) -> bool:
    user_search = v_kinder_base.get_or_edit_a_record_from_a_table(SearchParameters, user_id)
    if user_search:
        user = v_kinder_base.get_or_edit_a_record_from_a_table(People, user_id)
        if date.today() - timedelta(days=30) >= user.date_of_change:
            info_users_vk = info_peoples(user_id=user_id)
            v_kinder_base.add_peoples_to_a_tables(info_users_vk)
        return True
    else:
        vk_group.write_msg(user_id, message=message['the_first_greeting'], keyboard=interface_main())
        info_users_vk = info_peoples(user_id=user_id)
        v_kinder_base.add_peoples_to_a_tables(info_users_vk)
        new_user_search_parameters = default_search_parameters(info_users_vk)
        v_kinder_base.add_a_record_to_a_table(SearchParameters, **new_user_search_parameters)
        print('Параметры по умолчанию созданы')
        return False


def search(user_id: int):
    """Функция получает случайного человека (пользователя 'Вконтакте') и опровляет в чат 'user_id' 3 самых популярных
    фотографии. Так же в функции проверяется и обновляется информация о пользователе"""
    today = date.today()
    user_search_parameters = v_kinder_base.get_or_edit_a_record_from_a_table(SearchParameters, user_id)
    city_title = user_search_parameters.city_title
    country_title = user_search_parameters.country_title
    sex_id = user_search_parameters.sex_id
    age_from = user_search_parameters.age_from
    age_to = user_search_parameters.age_to
    relations_id = user_search_parameters.relations_id
    interest = user_search_parameters.interest
    music = user_search_parameters.music
    movie = user_search_parameters.movie
    tv = user_search_parameters.tv
    book = user_search_parameters.book
    date_of_change = user_search_parameters.date_of_change
    search_of_vk = user_search_parameters.search_of_vk
    if not search_of_vk or today - timedelta(days=30) >= date_of_change:
        kwargs = dict(hometown=city_title, sex=sex_id, age_from=age_from, age_to=age_to)
        kwargs = {key: value for key, value in kwargs.items() if value}
        info_users_vk = info_peoples(**kwargs)
        v_kinder_base.add_peoples_to_a_tables(info_users_vk)
        v_kinder_base.get_or_edit_a_record_from_a_table(SearchParameters, user_id, edit=True, search_of_vk=True)
        print('Обновление базы данных по запросу прошло успешно!!!')
    kwargs = {'sex_id': sex_id, 'relations_id': relations_id, 'city_title': city_title, 'country_title': country_title,
              'interest': interest, 'music': music, 'movie': movie, 'tv': tv, 'book': book}
    if age_to:
        kwargs['b_date_from'] = b_date_age(age_to+1)
    if age_from:
        kwargs['b_date_to'] = b_date_age(age_from)
    peoples = v_kinder_base.request_peoples_id_db(user_id, **kwargs)
    if len(peoples) == 0:
        vk_group.write_msg(user_id, message='По вашим параметрам запроса не кого не найденно.'
                                            ' Попробуйте изменить параметры поиска')
        return
    error_checking = False
    people = list_photos = None
    while not error_checking:
        people = choice(peoples)
        list_photos = vk_user.popular_user_photos(people.id)
        if list_photos:
            error_checking = True
    if today - timedelta(days=30) >= people.date_of_change:
        info_users_vk = info_peoples(user_id=people.id)
        v_kinder_base.add_peoples_to_a_tables(info_users_vk)
    if people.blacklist is None:
        v_kinder_base.add_a_record_to_a_table(PeopleSearchParameters, user_id=user_id,
                                              people_id=people.id)
    first_name = people.first_name if people.first_name else ''
    last_name = people.last_name if people.last_name else ''
    age = str(age_b_date(people.date_of_birth)) if people.date_of_birth else ''
    city_title = people.city_title if people.city_title else ''
    message_name_age = '\n'.join([first_name + ' ' + last_name, age, city_title])
    for photo in list_photos:
        url = photo['url_max'].split('?', 0)[0]
        response = vk_group.vk_session.method('photos.getMessagesUploadServer')
        photo_b = requests.get(url).content
        response = requests.post(response['upload_url'], files={'photo': ('.jpeg', photo_b)}).json()
        response = vk_group.vk_session.method('photos.saveMessagesPhoto', values={'photo': response['photo'],
                                                                                  'server': response['server'],
                                                                                  'hash': response['hash']})[0]
        attachment = f'photo{response["owner_id"]}_{response["id"]}_{response["access_key"]}'
        vk_group.write_msg(user_id, attachment=attachment, keyboard=interface_search_result_photo(photo['path']))
    vk_group.write_msg(user_id, message=message_name_age, keyboard=interface_button_open_blacklist(people.id))


def search_parameters(user_id: int):
    user_search = v_kinder_base.get_or_edit_a_record_from_a_table(SearchParameters, user_id)
    message_list = ['***Параметры поиска***', f'Город: {user_search.city_title}',
                    f'Страна: {user_search.country_title}', f'Пол: {user_search.sex_id}',
                    f'Возраст от: {user_search.age_from}', f'Возраст до: {user_search.age_to}',
                    f'Статус: {user_search.relations_id}', f'Увлечения: {user_search.interest}',
                    f'Музыка: {user_search.music}', f'Фильмы: {user_search.movie}',
                    f'ТВ: {user_search.tv}', f'Книги: {user_search.book}']
    vk_group.write_msg(user_id, message='\n🔹'.join(message_list), keyboard=interface_parameters())


def change_search_parameters(user_id: int):
    vk_group.write_msg(user_id, message=message['change_parameters'], keyboard=interface_search_parameters())


def change_parameters(user_id: int, text: str, parameter: str):
    if text in ['👨 мужчин', '👩 женщин', '👤 незадано', '❎ сбросить_значение_параметра']:
        command_to_check_changes_in_search_parameters(user_id, text, parameter)
    elif text == '🚷 чёрный список':
        payload = json.loads(parameter)
        people_id = payload.get('params')
        blacklist(user_id, people_id)
    else:
        vk_group.write_msg(user_id, message=message[text], keyboard=interface_change_parameters(text),
                           payload=parameter)


def command_to_check_changes_in_search_parameters(user_id: int, text: str, payload: Optional[str]):

    if payload:
        payload = json.loads(payload)
        command = payload['command']
        value = payload.get('params')
        if value == 'сбросить':
            value = None
        else:
            text = text.strip()
            if command in ['🏡 город', '🌏 страна', '🎨 увлечения', '🎤 музыка', '🎥 фильмы', '📺 ТВ', '📖 книги']:
                value = text
            elif command in ['👶 возраст от', '🧓 возраст до']:
                if text.isdigit():
                    value = text
                else:
                    vk_group.write_msg(user_id, message=message_error['age'], keyboard=interface_search_parameters())
                    return
            elif command == '👥 статус':
                pattern = r'[0-8]{1}'
                value = ', '.join(sorted(set(re.findall(pattern, text))))
                if len(value) == 0:
                    vk_group.write_msg(user_id, message=message_error['relations'],
                                       keyboard=interface_search_parameters())
                    return
        kwargs = {column_name[command]: value}
        res = None
        if not value or len(value) > 0:
            res = v_kinder_base.get_or_edit_a_record_from_a_table(SearchParameters, user_id, edit=True, **kwargs)
        param = command.rsplit(' ', 1)[-1]
        if res:
            value = text.rsplit(' ', 1)[-1] if command == '👫 пол' else value
            vk_group.write_msg(user_id, message=f'Параметр "{param}" изменён на "{value}"',
                               keyboard=interface_search_parameters())
        else:
            vk_group.write_msg(user_id, message=f'При попытке изменить параметр "{param}" произошла ошибка',
                               keyboard=interface_search_parameters())
    else:
        vk_group.write_msg(user_id, message=message['greeting'], keyboard=interface_main())


def blacklist(user_id, people_id):
    """Функция добовляет человека 'people_id' в чёрный список пользователя 'user_id'"""
    v_kinder_base.get_or_edit_a_record_from_a_table(PeopleSearchParameters, [user_id, people_id], edit=True,
                                                    blacklist=True)
    people = v_kinder_base.get_or_edit_a_record_from_a_table(People, people_id)
    name = f'{people.first_name} {people.last_name}'
    vk_group.write_msg(user_id, message=f'Пользователь ({name}) добвлен в чёрный список')


def abort(user_id):
    vk_group.write_msg(user_id, message='Команда прервана', keyboard=interface_main())


def info_peoples(user_id: Optional[int] = None, hometown: Optional[str] = None,
                 sex: Optional[int] = None, relation: Optional[int] = None,
                 age_from: int = 0, age_to: int = 150) -> InfoPeoplesDB:
    """Функция преобразует информацию о пользователе 'ВКонтакте' b преобразует для дальнейшей загрузки в базу данных'"""
    if user_id:
        info_users_vk = vk_group.user_info(user_id=user_id)
    else:
        info_users_vk = vk_user.users_search(hometown=hometown, sex=sex, relation=relation,
                                             age_from=age_from, age_to=age_to)
    tables = ('people', 'city', 'country')
    result = dict.fromkeys(tables, {})
    for info_user_vk in info_users_vk:
        user_id = info_user_vk.get('id')
        city_id = None
        for table in tables:
            record = {}
            if table == 'people':
                b_date = info_user_vk.get('bdate')
                try:
                    date_of_birth = datetime.strptime(b_date, "%d.%m.%Y").date()
                except Exception as error_info:
                    date_of_birth = None
                    print(error_info)
                    print(f'Некоректная дата: "{b_date}"')
                record = {'id': user_id, 'first_name': info_user_vk.get('first_name'),
                          'last_name': info_user_vk.get('last_name'), 'sex_id': info_user_vk.get('sex'),
                          'date_of_birth': date_of_birth, 'relation_id': info_user_vk.get('relation'),
                          'interests': info_user_vk.get('interests'), 'music': info_user_vk.get('music'),
                          'movies': info_user_vk.get('movies'), 'tv': info_user_vk.get('tv'),
                          'books': info_user_vk.get('books')}
            elif table == 'city':
                record = info_user_vk.get(table)
                if record:
                    city_id = record['id']
                    result['people'][user_id]['city_id'] = city_id
            elif table == 'country':
                record = info_user_vk.get(table)
                if record and city_id:
                    result['city'][city_id]['country_id'] = record['id']
            if record:
                id_ = record['id']
                result[table] = {**result[table], **{id_: {key: value for key, value in record.items() if value}}}
    return result


def default_search_parameters(info: InfoPeoplesDB):
    """Функция создаёт параметры поиска по умолчанию"""
    user_info = list(info['people'].values())[0]
    b_data = user_info.get('date_of_birth')
    age_from = age_to = None
    if b_data:
        age = age_b_date(user_info['date_of_birth'])
        age_from = age - 5
        age_to = age + 5
    record = {'id': user_info['id'], 'age_from': age_from, 'age_to': age_to, 'relations_id': '0, 1, 6',
              'interests': user_info.get('interests'), 'music': user_info.get('music'), 'movie': user_info.get('movie'),
              'tv': user_info.get('tv'), 'book': user_info.get('book')}
    sex_id = user_info.get('sex_id')
    if sex_id == 1:
        record.update({'sex_id': 2})
    elif sex_id == 2:
        record.update({'sex_id': 1})
    else:
        record.update({'sex_id': 0})
    for table in ['city', 'country']:
        res = list(info[table].values())
        if len(res) == 1:
            record[f'{table}_title'] = res[0].get('title')
    return {key: value for key, value in record.items() if value}


def age_b_date(b_data: date) -> int:
    """Функция определяет возраст по дате рождения"""
    today = date.today()
    return today.year - b_data.year - ((today.month, today.day) < (b_data.month, b_data.day))


def b_date_age(age: int) -> date:
    """Функция возрощает дату из колличества лет назад"""
    today = date.today()
    return date(today.year - age, today.month, today.day)
