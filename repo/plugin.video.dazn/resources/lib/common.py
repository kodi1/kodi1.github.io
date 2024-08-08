# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode, py2_decode
from six.moves.urllib.parse import urlencode

import _strptime

from base64 import b64decode
from calendar import timegm
from datetime import date, datetime, timedelta
from hashlib import md5
from inputstreamhelper import Helper
from json import dump, load, loads
from os.path import join
from platform import uname
from string import capwords
from time import mktime, sleep, strptime
from uuid import UUID

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer


class Common():


    def __init__(self, addon=None, addon_handle=None, addon_url=None):
        self.api_base = 'https://isl.dazn.com/misl/'
        self.api_img_base = 'https://images.discovery.indazn.com/eu/v2/eu/image'
        self.time_format = '%Y-%m-%dT%H:%M:%SZ'
        self.date_format = '%Y-%m-%d'
        self.portability_list = ['AT', 'DE', 'IT', 'ES']

        self.addon = addon
        self.addon_handle = addon_handle
        self.addon_url = addon_url
        self.addon_id = self.addon.getAddonInfo('id')
        self.addon_name = self.addon.getAddonInfo('name')
        self.addon_version = self.addon.getAddonInfo('version')
        self.addon_icon = self.addon.getAddonInfo('icon')
        self.addon_fanart = self.addon.getAddonInfo('fanart')
        self.content = self.addon.getSetting('content')
        self.view_id = self.addon.getSetting('view_id')
        self.view_id_videos = self.addon.getSetting('view_id_videos')
        self.view_id_epg = self.addon.getSetting('view_id_epg')
        self.force_view = self.addon.getSetting('force_view') == 'true'
        self.startup = self.addon.getSetting('startup') == 'true'
        self.select_cdn = self.addon.getSetting('select_cdn') == 'true'
        self.preferred_cdn = self.addon.getSetting('preferred_cdn')
        self.max_bw = self.addon.getSetting('max_bw')
        self.resources = self.addon.getSetting('api_endpoint_resource_strings')
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        self.android_properties = {}

        self.railCache = StorageServer.StorageServer(py2_encode('{0}.rail').format(self.addon_id), 24 * 7)


    def log(self, msg):
        xbmc.log(str(msg), xbmc.LOGDEBUG)


    def build_url(self, query):
        return self.addon_url + '?' + urlencode(query)


    def gui_language(self):
        language = xbmc.getLanguage().split(' (')[0]
        return xbmc.convertLanguage(language, xbmc.ISO_639_1)


    def get_addon(self):
        return self.addon


    def get_datapath(self):
        return py2_decode(xbmcvfs.translatePath(self.get_addon().getAddonInfo('profile')))


    def get_filepath(self, file_name):
        if file_name.startswith('http'):
            file_name = file_name.split('/')[-1]
        return join(self.get_datapath(), file_name)


    def get_dialog(self):
        return xbmcgui.Dialog()


    def set_setting(self, key, value):
        return self.get_addon().setSetting(key, value)


    def get_setting(self, key):
        return self.get_addon().getSetting(key)


    def get_string(self, id_):
        if id_ < 30000:
            src = xbmc
        else:
            src = self.get_addon()
        return src.getLocalizedString(id_)


    def dialog_ok(self, msg):
        self.get_dialog().ok(self.addon_name, msg)


    def dialog_yesno(self, msg):
        return self.get_dialog().yesno(self.addon_name, msg)


    def notification(self, title, msg, thumb, duration):
        self.get_dialog().notification(title, msg, thumb, duration)


    def b64dec(self, data):
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += py2_encode('=') * (4 - missing_padding)
        return b64decode(data)


    def get_resource(self, text, prefix=''):
        data_found = False
        data = self.get_cache(self.resources)
        if data.get('Strings'):
            strings = data['Strings']
            try:
                text = strings['{0}{1}'.format(prefix, text.replace(' ', ''))]
                data_found = True
            except KeyError:
                text = text.replace('_', ' ')
        return {'text': self.initcap(text), 'found': data_found}


    def logout(self):
        return self.dialog_yesno(self.get_resource('signout_body').get('text'))


    def time_now(self):
        return datetime.now().strftime(self.time_format)


    def time_stamp(self, str_date):
        return datetime.fromtimestamp(mktime(strptime(str_date, self.time_format)))


    def timedelta_total_seconds(self, timedelta):
        return int((timedelta.microseconds + (timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6)


    def utc2local(self, date_string):
        if str(date_string).startswith('2'):
            utc_dt = datetime(*(strptime(date_string, self.time_format)[0:6]))
            local_ts = timegm(utc_dt.timetuple())
            local_dt = datetime.fromtimestamp(local_ts)
            assert utc_dt.resolution >= timedelta(microseconds=1)
            return local_dt.replace(microsecond=utc_dt.microsecond).strftime(self.time_format)


    def uniq_id(self):
        if self.get_setting('device_id'):
            return self.get_setting('device_id')

        device_id = ''
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        # hack response busy
        i = 0
        while not py2_encode(':') in mac_addr and i < 3:
            i += 1
            sleep(1)
            mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        if py2_encode(':') in mac_addr:
            device_id = str(UUID(md5(mac_addr.encode('utf-8')).hexdigest()))
        elif xbmc.getCondVisibility('System.Platform.Android'):
            device_id = str(UUID(md5(self.get_android_uuid().encode('utf-8')).hexdigest()))

        if device_id == '':
            self.log('[{0}] error: failed to get device id ({1})'.format(self.addon_id, str(mac_addr)))
            self.dialog_ok(self.get_resource('error_4005_ConnectionLost').get('text'))
        self.set_setting('device_id', device_id)
        return device_id


    def open_is_settings(self):
        xbmcaddon.Addon(id='inputstream.adaptive').openSettings()


    def start_is_helper(self):
        helper = Helper(protocol='mpd', drm='widevine')
        return helper.check_inputstream()


    def days(self, title, now, start):
        if start and not title == 'Live':
            today = date.today()
            if now[:10] == start[:10]:
                return self.get_resource('tileLabelToday', 'browseui_').get('text')
            elif str(today + timedelta(days=1)) == start[:10]:
                return self.get_resource('tileLabelTomorrow', 'browseui_').get('text')
            else:
                for i in range(2, 8):
                    if str(today + timedelta(days=i)) == start[:10]:
                        return self.get_resource((today + timedelta(days=i)).strftime('%A'), 'calendar_').get('text')
        return self.get_resource(title, 'browseui_').get('text')


    def epg_date(self, date):
        return datetime.fromtimestamp(mktime(strptime(date, self.date_format)))


    def get_prev_day(self, date):
        return (date - timedelta(days=1))


    def get_next_day(self, date):
        return (date + timedelta(days=1))


    def get_date(self):
        date = 'today'
        dlg = self.get_dialog().numeric(1, self.get_string(30230))
        if dlg:
            spl = dlg.split('/')
            date = '%s-%s-%s' % (spl[2], spl[1], spl[0])
        return date


    def get_max_registrable_devices(self, token):
        token_data = loads(self.b64dec(token.split('.')[1]))
        maxRegistrableDevices = token_data.get('entitlements', {}).get('features', {}).get('DEVICE', {}).get('max_registered_devices', 6)

        return maxRegistrableDevices


    def get_entitlements(self, token):
        entitlements = []

        token_data = loads(self.b64dec(token.split('.')[1]))
        entitlementSets = token_data.get('entitlements', {}).get('entitlementSets', [])
        if entitlementSets:
            entitlements.extend(entitlementSets[0].get('entitlements', []))

        return entitlements


    def language(self, language, languages):
        gui_lang = self.gui_language()
        for i in languages:
            if i.lower() == gui_lang.lower():
                language = i
                break
        return language


    def portability_country(self, country, user_country):
        if user_country in self.portability_list:
            country = user_country
        return country


    def get_cache(self, file_name):
        json_data = {}
        file_ = self.get_filepath(file_name)
        if xbmcvfs.exists(file_):
            try:
                f = xbmcvfs.File(file_, 'r')
                json_data = load(f)
                f.close()
            except Exception as e:
                self.log("[{0}] get cache error: {1}".format(self.addon_id, e))
        return json_data


    def cache(self, file_name, data):
        file_ = self.get_filepath(file_name)
        try:
            f = xbmcvfs.File(file_, 'w')
            dump(data, f)
            f.close()
        except Exception as e:
            self.log("[{0}] cache error: {1}".format(self.addon_id, e))


    def split_on_uppercase(self, s, keep_contiguous=False):
        string_length = len(s)
        is_lower_around = (lambda: s[i - 1].islower() or
                           string_length > (i + 1) and s[i + 1].islower())

        start = 0
        parts = []
        for i in range(1, string_length):
            if s[i].isupper() and (not keep_contiguous or is_lower_around()):
                parts.append(s[start: i])
                start = i
        parts.append(s[start:])

        return parts


    def initcap(self, text):
        if text.isupper() and len(text) > 3:
            text = capwords(text)
            text = text.replace('Dazn', 'DAZN')
        elif not text.isupper() and not ' ' in text:
            parts = self.split_on_uppercase(text, True)
            text = ' '.join(parts)
        return text


    def get_cdn(self, cdns):
        if self.select_cdn:
            ret = self.get_dialog().select(self.get_string(30023), cdns)
            if not ret == -1:
                self.preferred_cdn = cdns[ret]
                self.set_setting('preferred_cdn', self.preferred_cdn)
                self.set_setting('select_cdn', 'false')
        return self.preferred_cdn


    def validate_pin(self, pin):
        result = False
        if len(pin) == 4 and pin.isdigit():
            result = True
        return result


    def youth_protection_pin(self, verify_age):
        pin = ''
        if verify_age:
            pin = self.get_dialog().input(self.get_resource('youthProtectionTV_verified_body').get('text'), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        return pin


    def get_dict_value(self, dict, key):
        key = key.lower()
        result = [dict[k] for k in dict if k.lower() == key]
        return result[0] if len(result) > 0 else ''


    def init_api_endpoints(self, service_dict):
        endpoint_dict = dict()
        endpoint_def_dict = dict(
                        api_endpoint_rail='Rail',
                        api_endpoint_rails='Rails',
                        api_endpoint_epg='Epg',
                        api_endpoint_event='Event',
                        api_endpoint_playback='Playback',
                        api_endpoint_signin='SignIn',
                        api_endpoint_signout='SignOut',
                        api_endpoint_refresh_access_token='RefreshAccessToken',
                        api_endpoint_userprofile='UserProfile',
                        api_endpoint_resource_strings='ResourceStrings',
                        api_endpoint_devices='Devices'
                        )
        for key, value in endpoint_def_dict.items():
            last_key = list(service_dict.get(value).get('Versions'))[-1]
            service_path = service_dict.get(value).get('Versions').get(last_key).get('ServicePath')
            self.set_setting(key, service_path)
            endpoint_dict.update({key: service_path})
            if key == 'api_endpoint_resource_strings':
                self.resources = service_path

        return endpoint_dict


    def set_videoinfo(self, listitem, infolabels):

        videoinfotag = listitem.getVideoInfoTag()

        if infolabels.get('title') is not None:
            videoinfotag.setTitle(infolabels.get('title'))
        if infolabels.get('plot') is not None:
            videoinfotag.setPlot(infolabels.get('plot'))
        if infolabels.get('mpaa') is not None:
            videoinfotag.setMpaa(infolabels.get('mpaa'))
        if infolabels.get('genre') is not None:
            videoinfotag.setGenres(infolabels.get('genre'))
        if infolabels.get('studio') is not None:
            videoinfotag.setStudios(infolabels.get('studio'))
        if infolabels.get('episode') is not None:
            videoinfotag.setEpisode(infolabels.get('episode'))
        if infolabels.get('sortepisode') is not None:
            videoinfotag.setSortEpisode(infolabels.get('sortepisode'))
        if infolabels.get('tvshowtitle') is not None:
            videoinfotag.setTvShowTitle(infolabels.get('tvshowtitle'))
        if infolabels.get('premiered') is not None:
            videoinfotag.setPremiered(infolabels.get('premiered'))
        if infolabels.get('date') is not None:
            videoinfotag.setDateAdded(infolabels.get('date'))
        if infolabels.get('aired') is not None:
            videoinfotag.setFirstAired(infolabels.get('aired'))
        if infolabels.get('duration') is not None:
            videoinfotag.setDuration(infolabels.get('duration'))
        if infolabels.get('season') is not None:
            videoinfotag.setSeason(infolabels.get('season'))
        if infolabels.get('sortseason') is not None:
            videoinfotag.setSortSeason(infolabels.get('sortseason'))
        if infolabels.get('tagline') is not None:
            videoinfotag.setTagLine(infolabels.get('tagline'))
        if infolabels.get('mediatype') is not None:
            videoinfotag.setMediaType(infolabels.get('mediatype'))

        return listitem


    def set_streaminfo(self, listitem, streamlabels):

        videoinfotag = listitem.getVideoInfoTag()
        videostream = xbmc.VideoStreamDetail()

        if streamlabels.get('width') is not None:
            videostream.setWidth(streamlabels.get('width'))
        if streamlabels.get('height') is not None:
            videoinfotag.setHeight(streamlabels.get('height'))
        if streamlabels.get('aspect') is not None:
            videostream.setAspect(streamlabels.get('aspect'))
        if streamlabels.get('duration') is not None:
            videostream.setDuration(streamlabels.get('duration'))
        if streamlabels.get('codec') is not None:
            videostream.setCodec(streamlabels.get('codec'))
        if streamlabels.get('stereoMode') is not None:
            videostream.setStereoMode(streamlabels.get('stereoMode'))
        if streamlabels.get('language') is not None:
            videostream.setLanguage(streamlabels.get('language'))

        videoinfotag.addVideoStream(videostream)

        return listitem


    def get_user_agent(self):

        if self.user_agent:
            return self.user_agent

        # Fails on some systems
        try:
            os_uname = list(uname())
        except Exception:
            os_uname = ['Linux', 'hostname', 'kernel-ver', 'kernel-sub-ver', 'x86_64']

        user_agent_suffix = 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'

        # android
        if xbmc.getCondVisibility('System.Platform.Android'):
            user_agent = 'Mozilla/5.0 (Linux; Android {}; {}) {}'.format(
                    self.get_android_prop('ro.build.version.release', True) or '12',
                    self.get_android_prop('ro.product.model', True) or 'Pixel 6',
                    user_agent_suffix)

        # linux on arm uses widevine from chromeos
        elif os_uname[0] == 'Linux' and os_uname[4].lower().find('arm') != -1:
            user_agent = 'Mozilla/5.0 (X11; CrOS {} 14268.67.0) {}'.format(os_uname[4], user_agent_suffix)
        elif os_uname[0] == 'Linux':
            user_agent = 'Mozilla/5.0 (X11; Linux {}) {}'.format(os_uname[4], user_agent_suffix)
        elif os_uname[0] == 'Darwin':
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_1) {}'.format(user_agent_suffix)
        else:
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) {}'.format(user_agent_suffix)

        # self.user_agent = user_agent
        return user_agent


    def get_android_prop(self, key, exact_match=False):

        if xbmc.getCondVisibility('System.Platform.Android'):
            if len(self.android_properties.keys()) == 0:
                try:
                    from subprocess import check_output
                    prop_output = check_output(['/system/bin/getprop']).splitlines()
                    for prop in prop_output:
                        prop = prop.decode()
                        prop_k_v = prop.split(']: [')
                        if len(prop_k_v) == 2 and prop_k_v[0].startswith('[') and prop_k_v[1].endswith(']'):
                            self.android_properties.update({prop_k_v[0][1:]: prop_k_v[1][:-1]})
                    self.log('Found android properties {}'.format(self.android_properties))
                except Exception as e:
                    self.log('Getting android properties failed with exception: {}'.format(e))

            if exact_match is True and self.android_properties.get(key, None) is not None:
                return self.android_properties.get(key)
            else:
                for prop_key, prop_value in self.android_properties.items():
                    if prop_key.find(key) != -1:
                        return prop_value

            if exact_match is True:
                try:
                    from subprocess import check_output
                    prop_output = check_output(['/system/bin/getprop', key]).splitlines()
                    if len(prop_output) == 1 and len(prop_output) != 0:
                        prop = prop_output[0].decode()
                        self.android_properties.update({key: prop})
                        return prop
                except Exception as e:
                    self.log('Getting android property {} with exception: {}'.format(key, e))


    def get_android_uuid(self):
        from subprocess import PIPE as subprocess_PIPE, Popen as subprocess_Popen
        from re import sub as re_sub
        values = ''
        try:
            # Due to the new android security we cannot get any type of serials
            sys_prop = ['ro.product.board', 'ro.product.brand', 'ro.product.device', 'ro.product.locale'
                        'ro.product.manufacturer', 'ro.product.model', 'ro.product.platform',
                        'persist.sys.timezone', 'persist.sys.locale', 'net.hostname']
            # Warning net.hostname property starting from android 10 is deprecated return empty
            with subprocess_Popen(['/system/bin/getprop'], stdout=subprocess_PIPE) as proc:
                output_data = proc.communicate()[0].decode('utf-8')
            list_values = output_data.splitlines()
            for value in list_values:
                value_splitted = re_sub(r'\[|\]|\s', '', value).split(':')
                if value_splitted[0] in sys_prop:
                    values += value_splitted[1]
        except Exception:
            pass
        return values


    def get_max_bw(self):
        return self.max_bw
