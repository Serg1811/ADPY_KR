from vk_api import VkApi, VkUpload
from vk_api.requests_pool import VkRequestsPool
from vk_api.utils import get_random_id
from datetime import date


class VK:

    def __init__(self, token: str):
        self.token = token
        self.vk_session = VkApi(token=token)

    def write_msg(self, user_id, peer_id=None, message=None, attachment=None, keyboard=None,
                  template=None, payload=None):
        params = {'user_id': user_id,
                  'peer_id': peer_id,
                  'message': message,
                  'attachment': attachment,
                  'keyboard': keyboard,
                  'template': template,
                  'payload': payload,
                  'random_id': get_random_id()}
        params = {key: value for key, value in params.items() if value}
        self.vk_session.method('messages.send', params)

    def read_the_previous_message(self, user_id, peer_id=None, start_message_id=None, offset=2, count=1, rev=0,
                                  extended=0, group_id=None):
        """Метод читает сообщения диалога. По умолчанию предыдущее сообщение"""
        params = {'user_id': user_id,
                  'peer_id': peer_id,
                  'start_message_id': start_message_id,
                  'offset': offset,
                  'count': count,
                  'rev': rev,
                  'extended': extended,
                  'group_id': group_id}
        params = {key: value for key, value in params.items() if value}
        return self.vk_session.method('messages.getHistory', params)

    def user_info(self, user_id=None):
        params = {
            'fields': 'sex, bdate, city, country, interests, music, movies, tv, books, relation'
        }
        if user_id:
            params['user_id'] = user_id
        return self.vk_session.method('users.get', values=params)


class VkGroup(VK):

    def __init__(self, token: str):
        super().__init__(token)
        self.vk_session = VkApi(token=token)
        self.upload = VkUpload(self.vk_session.get_api())


class VkUser(VK):

    def __init__(self, token: str):
        super().__init__(token)
        self.vk_session = VkApi(token=token)

    def users_search(self, q=None, sort=0, offset=None, count=1000, city=None, hometown=None, country=None, sex=None,
                     relation=None, age_from=0, age_to=150):
        params = {'q': q,
                  'sort': sort,
                  'offset': offset,
                  'count': count,
                  'city': city,
                  'hometown': hometown,
                  'country': country,
                  'sex': sex,
                  'status': relation,
                  'fields': 'sex, bdate, city, country, interests, music, movies, tv, books, relation'
                  }
        params = {key: value for key, value in params.items() if value}
        responses = []
        if age_to != age_from:
            number_of_requests = (age_to - age_from) // 25
            for number in range(number_of_requests + 1):
                age_from_ = number * 25 + age_from
                age_to_ = age_to if number == number_of_requests else age_from + 24
                responses_ = []
                with VkRequestsPool(self.vk_session) as pool:
                    for age in range(age_from_, age_to_ + 1):
                        params['age_from'] = params['age_to'] = age
                        response = pool.method('users.search', values=params)
                        responses_ += [{'params': params, 'response': response}]
                responses += responses_
        else:
            with VkRequestsPool(self.vk_session) as pool:
                for month in range(1, 13):
                    params['age_from'] = params['age_to'] = age_from
                    params['birth_month'] = month
                    response = pool.method('users.search', values=params)
                    responses += [{'params': params, 'response': response}]
        results = []
        for key, value in enumerate(responses):
            result = value['response'].result
            if result['count'] > 1000 and value['params']['age_from'] != value['params']['age_to']:
                result += self.users_search(self, value['params'])

            else:
                age = value['params']['age_from']
                for item in result['items']:
                    b_date = item.get('bdate')
                    if b_date and len(b_date.split('.')) == 2:
                        item['bdate'] = f'{b_date}.{date.today().year - age}'
                results += result['items']
        return results

    def photos_get(self, owner_id=None, album_id='profile', count=5, offset=0):
        params = {
            'owner_id': owner_id,
            'album_id': album_id,
            'rev': 1,
            'extended': 1,
            'offset': offset,
            'count': count,
            'photo_sizes': 1
        }
        return self.vk_session.method('photos.get', values=params)

    def photos_get_user_photos(self, user_id=None, count=5, offset=0):
        params = {'user_id': user_id,
                  'sort': 0,
                  'extended': 1,
                  'offset': offset,
                  'count': count,
                  'photo_sizes': 1}
        return self.vk_session.method('photos.getUserPhotos', values=params)

    def popular_user_photos(self, user_id, album_id='profile', quantity=3):
        params = {
            'owner_id': user_id,
            'album_id': album_id,
            'rev': 1,
            'extended': 1,
            'offset': 0,
            'count': 1000,
            'photo_sizes': 1
        }
        try:
            resp = self.vk_session.method('photos.get', values=params)
        except Exception as error_info:
            print(f'Ошибка: {error_info}')
            return False
        photos_info = []
        for photo_info in resp['items']:
            photos_info += [
                {'id': f"{user_id}_{photo_info['id']}",
                 'path': f"https://vk.com/id{user_id}?{photo_info['sizes'][-1]['type']}"
                 f"=photo{user_id}_{photo_info['id']}",
                 'url_max': photo_info['sizes'][-1]['url'],
                 'likes': photo_info['likes']['count'],
                 'comments': photo_info['comments']['count']
                 }
            ]
        if len(photos_info) == 0:
            print('По запросу фотографий не найденно')
        return sorted(photos_info, key=lambda row: (row['likes'], row['comments']), reverse=True)[: quantity]
