import requests
import json

class voyo_napi:
    def __init__(self, settings):
        requests.packages.urllib3.disable_warnings()
        self.__settings = settings
        self.__ses = requests.session()
        self.__res = 0

    def login(self):
        formdata = { "username": self.__settings['username'], "password": self.__settings['password']}
        headers = {
             "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
             "Accept": "application/json, text/plain, */*"      
                   }
        self.__res = self.__ses.post('https://napi.voyo.bg/api/bg/v1/login',
            headers=headers, data=formdata, verify=False)
        if self.__res.status_code == 200:
            self.__auth_data = json.loads(self.__res.text)
            return True
        return False

    def info(self):
        headers = {
            'Authorization': 'Bearer ' + self.__auth_data['credentials']['accessToken']
            }
        self.__res = self.__ses.get('https://napi.voyo.bg/api/bg/v1/users/info', headers=headers)
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None
    
    def tv(self):
        self.__res = self.__ses.get('https://napi.voyo.bg/api/bg/v1/tv')
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None

    def categories(self, cat_id, sort, page):
        url = f'https://napi.voyo.bg/api/bg/v1/content/filter?category={cat_id}'
        if sort:
            url += '&sort=date-desc'
        if page:
            url += f'&page={page}'
        self.__res = self.__ses.get(url)
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None

    def search(self, text):
        self.__res = self.__ses.get(f'https://napi.voyo.bg/api/bg/v1/search?query={text}')
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None

    def product_info(self, product_id):
        headers = {
             "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
             "Accept": "application/json, text/plain, */*",
             "Accept-Encoding": "gzip, deflate, br"
                   }

        self.__res = self.__ses.get(f'https://napi.voyo.bg/api/bg/v1/products/{product_id}')
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None

    def episodes(self, product_id, page=1):
        self.__res = self.__ses.get(f'https://napi.voyo.bg/api/bg/v1/products/{product_id}/episodes?page={page}&pagesize=24&sort=episode-desc')
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None

    def get_play_link(self, product_id):
        headers = {'Authorization': 'Bearer ' + self.__auth_data['credentials']['accessToken'] }
        self.__res = self.__ses.post(f'https://napi.voyo.bg/api/bg/v1/products/{product_id}/plays?acceptVideo=drm-widevine', headers=headers)
        if self.__res.status_code == 200:
            j = self.__res.json()
            return j
        return None


    def sections(self):
        sect_list = []
        self.__res = self.__ses.get('https://voyo.bg/manifest.json')
        if self.__res.status_code == 200:
            res = self.__res.json()
            return res['shortcuts']
