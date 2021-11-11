import requests
import time
import json
import datetime
from pprint import pprint
from progress.bar import IncrementalBar

def get_token(file):
    with open(file) as file_object:
        token = file_object.readline().strip()
        token_yd = file_object.readline().strip()
        return token, token_yd

class VkUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version    
        }

    def get_photo(self, location):
        user=input('Введите id или имя пользователя: ')
        count=input('Введите количество фотографий, которые необходимо загрузить: ')
        get_photo_url = self.url + 'photos.get'
        get_user_url = self.url + 'users.search'
        if not user.isdigit():
            get_user_params = {
                'q': user,
                'count':'1',
                'has_photo':'1'
            }
            res_user = requests.get(get_user_url, params={**self.params, **get_user_params}).json()
            get_photo_params = {
                'owner_id':res_user['response']['items'][0]['id'],
                'extended': '1',
                'album_id':location,
                'photo_sizes':'1',
                'count': count
            }
        else:
            get_photo_params = {
                'owner_id':user,
                'extended': '1',
                'album_id':location,
                'photo_sizes':'1',
                'count': count
            }
        res_photo = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()
        return res_photo   
    
    def post_yd(self, name, location, token_yd, file_name='Photo.txt'):
        Photo_dict = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': 'OAuth ' + token_yd
        } 
        for i in self.get_photo(location)['response']['items']:
            for el in i['sizes']:
                if el['type'] == 'r':
                    if  str(i['likes']['count']) not in Photo_dict.values():
                        Photo_dict[el['url']] = str(i['likes']['count'])                       
                    else:
                        Photo_dict[el['url']] = str(i['likes']['count']) + datetime.datetime.fromtimestamp(i['date']).strftime('%Y-%m-%d-%H:%M:%S')[:10]
            
        bar = IncrementalBar('Countdown', max = len(Photo_dict))
        with open(file_name, 'a') as outfile:
            json.dump(Photo_dict, outfile)
        for k, v in Photo_dict.items():
            bar.next()
            time.sleep(1)
            params = {
                'path': name + '/'+ v,
                'url': k
            } 
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            r = requests.post(url=url, params=params, headers=headers)
            bar.finish()
        res = r.json()
        return res


class YandexDisk:
    def __init__(self, token_yd):
        self.token = token_yd

    def create_dir(self, name):
        headers = {
            "Accept": "application/json",
            "Authorization": "OAuth " + self.token
        } 
        params = {
            'path':name
        } 
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        response = requests.put(url=url, params=params, headers=headers)
        response.raise_for_status()
        if response.status_code == 201:
            print("Success")
    

if __name__ == '__main__':
    ya = YandexDisk(token_yd = get_token('token.txt')[1])
    ya.create_dir('PhotoVK')

    vk_client = VkUser(token=get_token('token.txt')[0], version='5.131')
    vk_client.post_yd('PhotoVK', 'profile', get_token('token.txt')[1])
    vk_client.post_yd('PhotoVK','wall', get_token('token.txt')[1])
    vk_client.post_yd('PhotoVK','saved', get_token('token.txt')[1])
  


