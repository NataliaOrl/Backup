import requests
import time
from pprint import pprint
from progress.bar import IncrementalBar

with open('token.txt') as file_object:
    token = file_object.readline().strip()
    token_yd = file_object.readline().strip()


class VkUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version    
        }

    def get_photo(self, location):
        get_photo_url = self.url + 'photos.get'
        get_photo_params = {
            'extended': '1',
            'album_id':location,
            'photo_sizes':'1'
        }
        res_photo = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()
        return res_photo   
    
    def post_yd(self, token_yd, location, name):
        Photo_dict = {}
        headers = {
                "Accept": "application/json",
                "Authorization": "OAuth " + token_yd
            } 
        for i in self.get_photo(location)['response']['items']:
            for el in i['sizes']:
                if el['type'] == 'r':
                    if  str(i['likes']['count']) not in Photo_dict.values():
                        Photo_dict[el['url']] = str(i['likes']['count'])                       
                    else:
                        Photo_dict[el['url']] = str(i['likes']['count']) + str(i['date'])
        bar = IncrementalBar('Countdown', max = len(Photo_dict))         
        for k, v in Photo_dict.items():
            bar.next()
            time.sleep(1)
            params = {
                    'path': name + '/'+ v,
                    'url': k
                    } 
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            r = requests.post(url=url, params=params, headers=headers)
            bar.finish()
        res = r.json()
        return res

class YandexDisk:
    def __init__(self):
        self.token = token_yd

    def create_dir(self, name):
        headers = {
                "Accept": "application/json",
                "Authorization": "OAuth " + token_yd
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
    ya = YandexDisk()
    ya.create_dir('PhotoVK')
    vk_client = VkUser(token, '5.131')
    vk_client.post_yd(token_yd, 'profile', 'PhotoVK')
    vk_client.post_yd(token_yd, 'wall', 'PhotoVK')
    vk_client.post_yd(token_yd, 'saved', 'PhotoVK')


