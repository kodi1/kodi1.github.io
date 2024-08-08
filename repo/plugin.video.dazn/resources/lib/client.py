# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .simple_requests.api import Request


class Client:


    def __init__(self, plugin, credential):
        self.plugin = plugin
        self.credential = credential

        self.DEVICE_ID = self.plugin.get_setting('device_id')
        self.TOKEN = self.plugin.get_setting('token')
        self.COUNTRY = self.plugin.get_setting('country')
        self.LANGUAGE = self.plugin.get_setting('language')
        self.PORTABILITY = self.plugin.get_setting('portability')
        self.MAX_REGISTRABLE_DEVICES = self.plugin.get_setting('max_registrable_devices')
        self.ENTITLEMENTS = self.plugin.get_setting('entitlements').split(',')
        self.POST_DATA = {}
        self.ERRORS = 0

        self.HEADERS = {
            'Content-Type': 'application/json',
            'Referer': self.plugin.api_base
        }

        self.PARAMS = {}

        self.STARTUP = 'https://startup.core.indazn.com/misl/v5/Startup'
        self.RAIL = self.plugin.get_setting('api_endpoint_rail')
        self.RAILS = self.plugin.get_setting('api_endpoint_rails')
        self.EPG = self.plugin.get_setting('api_endpoint_epg')
        self.EVENT = self.plugin.get_setting('api_endpoint_event')
        self.PLAYBACK = self.plugin.get_setting('api_endpoint_playback')
        self.SIGNIN = self.plugin.get_setting('api_endpoint_signin')
        self.SIGNOUT = self.plugin.get_setting('api_endpoint_signout')
        self.REFRESH = self.plugin.get_setting('api_endpoint_refresh_access_token')
        self.PROFILE = 'https://user-profile.ar.indazn.com/v1/UserProfile'  # self.plugin.get_setting('api_endpoint_userprofile')
        self.RESOURCES = self.plugin.get_setting('api_endpoint_resource_strings')
        self.DEVICES = self.plugin.get_setting('api_endpoint_devices')


    def content_data(self, url):
        data = self.request(url)
        if data.get('odata.error', None):
            self.errorHandler(data)
        return data


    def rails(self, id_, params=''):
        self.PARAMS = {}
        self.PARAMS['country'] = self.COUNTRY
        self.PARAMS['groupId'] = id_
        self.PARAMS['params'] = params
        content_data = self.content_data(self.RAILS)
        for rail in content_data.get('Rails', []):
            id_ = rail.get('Id')
            resource = self.plugin.get_resource(id_, prefix='browseui_railHeader')
            title = resource.get('text')
            if resource.get('found') == False:
                rail_data = self.railFromCache(id_, rail.get('Params', params))
                title = rail_data.get('Title', rail.get('Id')) if isinstance(rail_data, dict) else rail.get('Id')
            else:
                title = resource.get('text')
            rail['Title'] = title
        return content_data


    def railFromCache(self, id_, params=''):
        return self.plugin.railCache.cacheFunction(self.rail, id_, params)


    def rail(self, id_, params=''):
        self.PARAMS = {}
        self.PARAMS['languageCode'] = self.LANGUAGE
        self.PARAMS['country'] = self.COUNTRY
        self.PARAMS['id'] = id_
        self.PARAMS['params'] = params
        return self.content_data(self.RAIL)


    def epg(self, params):
        self.PARAMS = {}
        self.PARAMS['languageCode'] = self.LANGUAGE
        self.PARAMS['country'] = self.COUNTRY
        self.PARAMS['date'] = params
        return self.content_data(self.EPG)


    def event(self, id_):
        self.PARAMS = {}
        self.PARAMS['languageCode'] = self.LANGUAGE
        self.PARAMS['country'] = self.COUNTRY
        self.PARAMS['id'] = id_
        return self.content_data(self.EVENT)


    def resources(self):
        self.PARAMS = {}
        self.PARAMS['languageCode'] = self.LANGUAGE
        self.PARAMS['region'] = self.COUNTRY
        self.PARAMS['platform'] = 'web'
        self.plugin.cache(self.RESOURCES, self.content_data(self.RESOURCES))


    def playback_data(self, id_):
        self.HEADERS['authorization'] = 'Bearer ' + self.TOKEN
        self.HEADERS['x-dazn-device'] = self.DEVICE_ID
        self.HEADERS['user-agent'] = self.plugin.get_user_agent()
        self.PARAMS = {}
        self.PARAMS['AssetId'] = id_
        self.PARAMS['PlayerId'] = 'test'
        self.PARAMS['DrmType'] = 'WIDEVINE'
        self.PARAMS['Platform'] = 'web'
        self.PARAMS['Format'] = 'MPEG-DASH'
        self.PARAMS['LanguageCode'] = self.LANGUAGE
        self.PARAMS['Model'] = 'N/A'
        self.PARAMS['Secure'] = 'true'
        self.PARAMS['Latitude'] = ''
        self.PARAMS['Longitude'] = ''
        self.PARAMS['Manufacturer'] = 'unknown'
        self.PARAMS['PlayReadyInitiator'] = 'false'
        self.PARAMS['MtaLanguageCode'] = self.LANGUAGE
        self.PARAMS['AppVersion'] = '9.41.0-hotfix.1.645'
        self.PARAMS['capabilities'] = 'mta'
        return self.request(self.PLAYBACK)


    def playback(self, id_, pin):
        if self.plugin.validate_pin(pin):
            self.HEADERS['x-age-verification-pin'] = pin
        data = self.playback_data(id_)
        if data.get('odata.error', None):
            self.errorHandler(data)
            if self.TOKEN:
                data = self.playback_data(id_)
        return data


    def userProfile(self):
        self.HEADERS['authorization'] = 'Bearer ' + self.TOKEN
        data = self.request(self.PROFILE)
        if data.get('odata.error', None):
            self.errorHandler(data)
        else:
            if 'PortabilityAvailable' in self.PORTABILITY:
                self.COUNTRY = self.plugin.portability_country(self.COUNTRY, data['UserCountryCode'])
                if not self.LANGUAGE.lower() == data['UserLanguageLocaleKey'].lower():
                    self.LANGUAGE = data['UserLanguageLocaleKey']
                    self.setLanguage(data['SupportedLanguages'])
            self.plugin.set_setting('viewer_id', data['ViewerId'])
            self.plugin.set_setting('language', self.LANGUAGE)
            self.plugin.set_setting('country', self.COUNTRY)
            self.plugin.set_setting('portability', self.PORTABILITY)


    def setLanguage(self, languages):
        self.LANGUAGE = self.plugin.language(self.LANGUAGE, languages)
        self.resources()


    def setToken(self, auth, result):
        self.plugin.log('[{0}] signin: {1}'.format(self.plugin.addon_id, result))
        if auth and result in ['SignedIn', 'SignedInInactive']:
            self.TOKEN = auth['Token']
            self.MAX_REGISTRABLE_DEVICES = self.plugin.get_max_registrable_devices(self.TOKEN)
            self.ENTITLEMENTS = self.plugin.get_entitlements(self.TOKEN)
        else:
            if result in ['HardOffer', 'SignedInPaused']:
                self.plugin.dialog_ok(self.plugin.get_resource('error_10101').get('text'))
            self.signOut()
        self.plugin.set_setting('token', self.TOKEN)
        self.plugin.set_setting('max_registrable_devices', '{}'.format(self.MAX_REGISTRABLE_DEVICES))
        self.plugin.set_setting('entitlements', ','.join(self.ENTITLEMENTS))


    def signIn(self):
        credentials = self.credential.get_credentials()
        if credentials:
            self.HEADERS['User-Agent'] = self.plugin.get_user_agent()
            self.HEADERS['x-dazn-ua'] = '{} {}'.format(self.plugin.get_user_agent(), 'signin/4.40.3.81 hyper/0.14.0 (web; production; de)')
            self.POST_DATA = {
                'Email': credentials['email'],
                'Password': credentials['password'],
                'DeviceId': self.DEVICE_ID,
                'Platform': 'web'
            }
            data = self.request(self.SIGNIN)
            if data.get('odata.error', None):
                self.errorHandler(data)
            else:
                self.setToken(data['AuthToken'], data.get('Result', 'SignInError'))
                if self.plugin.get_setting('save_login') == 'true' and self.plugin.get_setting('token'):
                    self.credential.set_credentials(credentials['email'], credentials['password'])
        else:
            self.plugin.dialog_ok(self.plugin.get_resource('signin_tvNoSignUpPerex').get('text'))


    def signOut(self):
        if self.TOKEN:
            self.HEADERS['authorization'] = 'Bearer ' + self.TOKEN
            self.POST_DATA = {
                'DeviceId': self.DEVICE_ID
            }
            r = self.request(self.SIGNOUT)
        self.TOKEN = ''
        self.plugin.set_setting('token', self.TOKEN)
        self.plugin.set_setting('device_id', '')


    def refreshToken(self):
        self.HEADERS['authorization'] = 'Bearer ' + self.TOKEN
        self.HEADERS['User-Agent'] = self.plugin.get_user_agent()
        self.POST_DATA = {
            'DeviceId': self.DEVICE_ID
        }
        data = self.request(self.REFRESH)
        if data.get('odata.error', None):
            self.signOut()
            self.errorHandler(data)
        else:
            self.setToken(data['AuthToken'], data.get('Result', 'RefreshAccessTokenError'))


    def playableDevices(self):
        self.HEADERS['authorization'] = 'Bearer ' + self.TOKEN
        data = self.request(self.DEVICES)
        if data.get('odata.error', None):
            self.errorHandler(data)
            return None
        else:
            playableDevices = 0
            for device in data.get('devices'):
                if device.get('playable'):
                    playableDevices += 1

            return playableDevices


    def initStartupData(self):
        self.POST_DATA = {
            'LandingPageKey': 'generic',
            'Languages': '{0}, {1}'.format(self.plugin.gui_language(), self.LANGUAGE),
            'Platform': 'web',
            'Manufacturer': '',
            'PromoCode': ''
        }
        return self.request(self.STARTUP)


    def initApiEndpoints(self, endpoints_dict):
        self.RAIL = endpoints_dict.get('api_endpoint_rail')
        self.RAILS = endpoints_dict.get('api_endpoint_rails')
        self.EPG = endpoints_dict.get('api_endpoint_epg')
        self.EVENT = endpoints_dict.get('api_endpoint_event')
        self.PLAYBACK = self.plugin.get_setting('api_endpoint_playback')
        self.SIGNIN = endpoints_dict.get('api_endpoint_signin')
        self.SIGNOUT = endpoints_dict.get('api_endpoint_signout')
        self.REFRESH = endpoints_dict.get('api_endpoint_refresh_access_token')
        # self.PROFILE = endpoints_dict.get('api_endpoint_userprofile')
        self.RESOURCES = endpoints_dict.get('api_endpoint_resource_strings')
        self.DEVICES = endpoints_dict.get('api_endpoint_devices')


    def initRegion(self, startup_data):
        region = startup_data.get('Region', {})
        if region:
            self.PORTABILITY = region['CountryPortabilityStatus']
            self.COUNTRY = region['Country']
            self.LANGUAGE = region['Language']
            self.setLanguage(startup_data['SupportedLanguages'])

        return region


    def startUp(self, region):
        if region.get('isAllowed', False):
            if self.TOKEN:
                self.refreshToken()
            else:
                self.signIn()
        else:
            self.TOKEN = ''
            self.plugin.log('[{0}] version: {1} region: {2}'.format(self.plugin.addon_id, self.plugin.addon_version, region))
            self.plugin.dialog_ok(self.plugin.get_resource('error_2003_notAvailableInCountry').get('text'))


    def request(self, url):
        requests = Request(self.plugin)
        if self.POST_DATA:
            r = requests.post(url, headers=self.HEADERS, data=self.POST_DATA, params=self.PARAMS)
            self.POST_DATA = {}
        else:
            r = requests.get(url, headers=self.HEADERS, params=self.PARAMS)

        if r.text and self.plugin.get_dict_value(r.headers, 'content-type').startswith('application/json'):
            return r.json()
        else:
            if not r.status_code == 204:
                self.plugin.log('[{0}] error: {1} ({2}, {3})'.format(self.plugin.addon_id, url, str(r.status_code), self.plugin.get_dict_value(r.headers, 'content-type')))
            if r.status_code == -1:
                self.plugin.log('[{0}] error: {1}'.format(self.plugin.addon_id, r.text))
            return {}


    def errorHandler(self, data):
        self.ERRORS += 1
        msg = data['odata.error']['message']['value']
        code = str(data['odata.error']['code'])
        self.plugin.log('[{0}] version: {1} country: {2} language: {3} portability: {4}'.format(self.plugin.addon_id, self.plugin.addon_version, self.COUNTRY, self.LANGUAGE, self.PORTABILITY))
        self.plugin.log('[{0}] error: {1} ({2})'.format(self.plugin.addon_id, msg, code))

        error_codes = ['10006', '10008', '10450']
        pin_codes = ['10155', '10161', '10163']

        if code == '10000' and self.ERRORS < 3:
            self.refreshToken()
        elif (code == '401' or code == '10033') and self.ERRORS < 3:
            self.signIn()
        elif code == '3001':
            self.startUp()
        elif code == '10049':
            self.plugin.dialog_ok(self.plugin.get_resource('signin_errormessage').get('text'))
        elif code == '10450' and self.ERRORS < 3:
            if self.playableDevices() >= int(self.MAX_REGISTRABLE_DEVICES):
                self.plugin.dialog_ok(self.plugin.get_resource('error2_65_450_403_header').get('text'))
            else:
                self.refreshToken()
        elif code == '10801':
            self.plugin.dialog_ok(self.plugin.get_resource('error2_65_801_403_header').get('text'))
        elif code in error_codes:
            self.plugin.dialog_ok(self.plugin.get_resource('error_{0}'.format(code)).get('text'))
        elif code in pin_codes:
            self.TOKEN = ''
            self.plugin.dialog_ok(self.plugin.get_resource('error_{0}'.format(code)).get('text'))
