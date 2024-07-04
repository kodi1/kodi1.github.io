# -*- coding: utf-8 -*-
import sys
import os
import threading
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
from bs4 import BeautifulSoup
#from resources.lib.voyo_web_api import *
from resources.lib.voyo_napi import *
from resources.lib.epgprocess import *
if sys.version_info[0] > 2 or sys.version_info[0] == 2 and sys.version_info[1] >= 7:
    import inputstreamhelper
    tv_only = False
else:
    tv_only = True
if sys.version_info[0] == 2:
    from urllib import urlencode
    from urllib import quote_plus
    from urlparse import parse_qsl
else:
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
    from urllib.parse import parse_qsl
import uuid
import json
import codecs

config_par = ['username', 'password', 'device', 'useEPG', 'epgURL',
              'epgOffset', 'wrkdir' ]
settings = {}

_url = sys.argv[0]
_handle = int(sys.argv[1])
__addon__   = xbmcaddon.Addon()

def get_addon():
  return __addon__

def get_addon_id():
  return __addon__.getAddonInfo('id')

def get_addon_name():
  return __addon__.getAddonInfo('name').decode('utf-8')

def get_addon_version():
  return __addon__.getAddonInfo('version')

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def getUrl(keyval_pair):
    return '{0}?{1}'.format(_url, urlencode(keyval_pair))

def get_platform():
  platforms = [
    "Android",
    "Linux.RaspberryPi",
    "Linux",
    "XBOX",
    "Windows",
    "ATV2",
    "IOS",
    "OSX",
    "Darwin"
   ]

  for platform in platforms:
    if xbmc.getCondVisibility('System.Platform.{0}'.format(platform)):
      return platform
  return "Unknown"

def get_version():
    return xbmc.getInfoLabel("System.BuildVersion")

def get_prn(msg):
    if str(type(msg)) == "<type 'unicode'>":
        s = msg.encode('utf-8')
    else:
        s = str(msg)
    return s

def log_primitive(msg):
    if str(type(msg)) == "<type 'unicode'>":
        s = msg.encode('utf-8')
    else:
        s = str(msg)
    xbmc.log("{0} v{1} | {2}".format(get_addon_id(), get_addon_version(), s), xbmc.LOGDEBUG)

def log(msg):
    try:
        if str(type(msg)) == "<type 'list'>" or str(type(msg)) == "<type 'tuple'>":
            for m in msg:
                log_primitive(msg)
        elif str(type(msg)) == "<type 'dict'>":
            for key in msg:
                log_primitive('{0} : {1}'.format(
                    get_prn(key), get_prn(msg[key])))
        else:
            log_primitive(msg)

    except:
        try:
            import traceback
            er = traceback.format_exc(sys.exc_info())
            xbmc.log('%s | Logging failure: %s' % (get_addon_id(), er), xbmc.LOGDEBUG)
        except:
            pass

class voyobg:
    def __init__(self):
        self.__napi = voyo_napi(settings)

    def login(self):
        return self.__napi.login()

    def get_devices(self):
        return self.__api.list_devices()

    def check_device(self):
        return self.__api.device_allowed() or self.__api.device_add()

    def remove_device(self, dev_id):
        return self.__api.device_remove(dev_id)

    def sections(self):
        return self.__napi.sections()

    def tv_radio(self, href):
        return self.__napi.tv()

    def channel(self, href):
        return self.__napi.get_play_link(href)

    def episodes(self, product_id, page):
        return self.__napi.episodes(product_id, page)
    
    def process_page(self, id, s, p):
        return self.__napi.categories(id, s, p)

    def product_info(self, productId):
        return self.__napi.product_info(productId)

    def process_play_url(self, productId):
        return self.__napi.get_play_link(productId)


class voyo_plugin:
    def __init__(self):
        if sys.version_info[0] == 2:
            self.wrkdir = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
        else:
            self.wrkdir = xbmcvfs.translatePath(__addon__.getAddonInfo('profile'))
        self.getSettings()
        if 'wrkdir' in settings:
            swd = settings['wrkdir']
            if len(swd) > 0:
                self.wrkdir = swd
        log('workdir: {0}'.format(self.wrkdir))
        self.useEPG = settings['useEPG'].lower() == 'true'
        self.epgOffset = int(settings['epgOffset'])
        self.voyo = voyobg()
        if not tv_only and self.useEPG: #python 2.6 won't be able to download the epg
            self.epg = voyo_epg(self.wrkdir)
            self.epg.configure(self.wrkdir, settings['epgURL'], self.epgOffset)
            self.epg.run()
        loginAttemps = 0
        while not self.voyo.login() and loginAttemps < 3:
            loginAttemps += 1
            dialog = xbmcgui.Dialog()
            dialog.ok(u'Грешка', u'Некоректни данни за абонамент!')
            __addon__.openSettings()
            self.getSettings()

        logofname = '{0}logos.json'.format(self.wrkdir)
        if xbmcvfs.exists(logofname):
            with open(logofname, 'r') as f:
                logostr = f.read()
                self.logos = json.loads(logostr)
        else:
            self.logos = {}

        epgfname = '{0}epg.json'.format(self.wrkdir)
        if xbmcvfs.exists(epgfname):
            with codecs.open(epgfname, 'r', 'utf-8') as f:
                epgs = f.read()
                self.epg = json.loads(epgs)
        else:
            self.epg = {}


    def getSettings(self):
        for key in config_par:
            settings[key] = __addon__.getSetting(key)
        if len(settings['username']) == 0 or len(settings['password']) == 0:
            __addon__.openSettings()
            settings['username'] = __addon__.getSetting('username')
            settings['password'] = __addon__.getSetting('password')
        if len(settings['device']) == 0:
            settings['device'] = uuid.uuid4().hex
            __addon__.setSetting('device', settings['device'])
        for key in config_par:
            settings[key] = __addon__.getSetting(key)
        log(settings)

    def list_categories(self):
        xbmcplugin.setPluginCategory(_handle, 'Voyobg')
        xbmcplugin.setContent(_handle, 'videos')
        #categories = self.voyo.sections()
        categories = [
            { 'url' : '/tv-radio/', 'name' : 'Телевизия'},
            { 'url' : '/more/', 'name' : 'Предавания'},
            { 'url' : '/series/', 'name' : 'Сериали'},
            { 'url' : '/films/', 'name' : 'Филми'},
            { 'url' : '/kids/', 'name' : 'За децата'},
            { 'url' : '/concerts/', 'name' : 'Концерти'},
            { 'url' : '/sport/', 'name' : 'Спорт'}
        ]
        for cat in categories:
            link = cat['url']
            name = cat['name']
            desciption  = 'Voyo'
            if tv_only:
                if cat['url'] != '/tv-radio/':
                    continue
            li = xbmcgui.ListItem(label=name)
            li.setInfo('video', {'title': name,
                                        'genre': desciption,
                                        'mediatype': 'video'})
            url = get_url(action='listing_sections', category=link.replace('/', '_'))
            is_folder = True
            xbmcplugin.addDirectoryItem(_handle, url, li, is_folder)
        xbmcplugin.endOfDirectory(_handle)

    def list_item(self, name, link, img, plot, productId, act_str, meta_inf=None, page=None):
        log('{0} :  {1} - {2}'.format(name, link, img))
        li = xbmcgui.ListItem(label=name)
        art = { 'thumb': img, 'poster': img, 'banner' : img, 'fanart': img }
        li.setArt(art)
        info_labels = {'title': name, 'plot': plot}
        if meta_inf:
            info_labels.update(meta_inf)
        li.setInfo('video', info_labels)
        ctxtmenu = []
        ctxtmenu.append(('Информация', 'XBMC.Action(Info)'))
        li.addContextMenuItems(ctxtmenu)
        #dict_url = {'action' : act_str, 'category': link.replace('/', '_'),
        #            'name' : name, 'img' : img, 'plot' : plot, 'link' :link}
        dict_url = {'action' : act_str, 'category': link.replace('/', '_') }
        if meta_inf:
            dict_url.update(meta_inf)
        isDir = True
        if act_str == 'listing_tv':
            dict_url['name'] = name
            isDir = False
        dict_url['productId'] = productId
        if page:
            dict_url['page'] = page
        url = getUrl(dict_url)
        xbmcplugin.addDirectoryItem(_handle, url, li, isDir)

    def list_play_url(self, name, link, img, plot, meta_inf, play_param):
        log('{0}: {1} - {2}'.format(name, img, play_param['url']))
        if not (sys.version_info[0] > 2 or sys.version_info[0] == 2 and
                sys.version_info[1] >= 7):
            dialog = xbmcgui.Dialog()
            dialog.ok(
            u'Грешка',
            u'Вашето устройство не може да възпроизведе това видео.')
            return
        if play_param:
            headers = "User-agent: stagefright/1.2 (Linux;Android 6.0)"
            PROTOCOL = 'mpd'
            DRM = play_param['drm']['keySystem']
            is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
            if is_helper.check_inputstream():
                metaflds = ['genre', 'country', 'rating', 'year', 'duration',
                            'plot']
                li = xbmcgui.ListItem(label=name, path=play_param['url'])
                inf_labels = {}
                for mf in metaflds:
                    if mf in meta_inf:
                        inf_labels[mf] = meta_inf[mf]
                li.setInfo(type="Video", infoLabels=inf_labels)
                li.setArt({'thumb': img, 'icon': img, 'fanart': img})
                if sys.version_info[0] == 2:
                    li.setProperty('inputstreamaddon', 'inputstream.adaptive')
                else:
                    li.setProperty('inputstream', 'inputstream.adaptive')
                li.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                li.setProperty('inputstream.adaptive.stream_headers', headers)
                li.setProperty('inputstream.adaptive.license_type', DRM)
                #licURL = play_param['drm']['licenseUrl'] + '||R{SSM}|BJBwvlic'
                licURL = play_param['drm']['licenseUrl'] + '||R{SSM}|'
                li.setProperty('inputstream.adaptive.license_key', licURL)
                li.setProperty('inputstream.adaptive.media_renewal_time', '600')
                li.setMimeType('application/dash+xml')
                li.setProperty("IsPlayable", str(True))
                xbmcplugin.addDirectoryItem(_handle, play_param['url'], li)
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok(
            u'Грешка',
            u'Видеото не е налично.')

    def get_channel_epg(self, name, i):
        tvmapping = {
            'btv': "bTV", 'int': "bTVi", 'comedy': "bTVComedy",
            'cinema': "bTVCinema", 'action': "bTVAction", 'lady': "bTVLady",
            'ring': "RING", 'voyo-cinema':"VoyoCinema"
        }
        chan_epg = []
        epg_str = ''
        img = i
        if self.useEPG:
            if name in tvmapping:
                name = tvmapping[name]
            if name in self.logos:
                img = self.logos[name]
            if name in self.epg:
                chan_epg = self.epg[name]
            cnt = 0
            now = time.time()
            for it in chan_epg:
                start = time.mktime(
                    time.strptime(it[0].split()[0],'%Y%m%d%H%M%S'))
                stop = time.mktime(
                    time.strptime(it[1].split()[0],'%Y%m%d%H%M%S'))
                if sys.version_info[0] == 2:
                    title = it[2].encode('utf-8')
                else:
                    title = it[2]
                if (start < now and stop >= now) or (now < start):
                    cnt += 1
                    ln = '{0} {1}\n'.format(
                        time.strftime('%H:%M', time.localtime(start)),
                                            title)
                    epg_str += ln
                if cnt >= 8:
                    break
        return epg_str, img, name

    def play_tv(self, params):
        log('play_tv: params: {}'.format(params))
        #self.device_status()
        category = params['category']
        link = category.replace('_', '/')
        epg_name = params['name']
        productId = params['productId']
        tv_channel_info = self.voyo.channel(productId)
        name = tv_channel_info['content']['title']
        img = tv_channel_info['content']['image']
        play_url = tv_channel_info['url']
        protocol = tv_channel_info['videoType']
        epg_str, img, n = self.get_channel_epg(epg_name, img)
        li = xbmcgui.ListItem(label=name, path=play_url)
        li.setInfo(type="Video", infoLabels={'genre':'TV',
            'plot':epg_str })
        li.setArt({'thumb': img, 'icon': img, 'fanart': img})
        li.setProperty("IsPlayable", str(True))
        if sys.version_info[0] > 2 or sys.version_info[0] == 2 and sys.version_info[1] >= 7:
            headers = "User-agent: stagefright/1.2 (Linux;Android 6.0)"
            PROTOCOL = protocol
            is_helper = inputstreamhelper.Helper(PROTOCOL)
            if is_helper.check_inputstream():
                if sys.version_info[0] == 2:
                    li.setProperty('inputstreamaddon', 'inputstream.adaptive')
                else:
                    li.setProperty('inputstream', 'inputstream.adaptive')
                li.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
                li.setProperty('inputstream.adaptive.stream_headers', headers)
            else:
                log('inputstreamhelper check failed.')
        xbmc.Player().play(play_url, li)

    def list_content(self, params):
        #self.device_status()
        category = params['category']
        cat_link = category.replace('_', '/')
        xbmcplugin.setPluginCategory(_handle, category)
        xbmcplugin.setContent(_handle, 'videos')
        if 'page' in params:
            page = int(params['page']) + 1
        else:
            page = 1
        if cat_link == '/tv-radio/':
            action_str = 'listing_tv'
            content = self.voyo.tv_radio(cat_link)
            for cont in content['liveTvs']:
                product_id = cont['id'] 
                name = cont['name'] 
                link = cont['url'] 
                img = cont['logo']
                epg_str, img, name = self.get_channel_epg(name, img)
                self.list_item(name, link, img, epg_str, product_id, action_str)
            #for cont in content['liveRadios']:
            #    link = cont['url'] 
            #    product_id = link[14:][0:5]
            #    name = cont['name'] 
            #    img = cont['logo']
            #    epg_str, img, name = self.get_channel_epg(name, img)
            #    self.list_item(name, link, img, epg_str, product_id, action_str)
        else:
            action_str = 'listing_sections'
            categories = {
                '/kids/': [(20411, False)],
                '/concerts/': [(20404, False)],
                '/more/': [(20346,False)],
                '/sport/':[(20408,False),(20378,False)],
                '/films/':[(20344,True)],
                '/series/':[(20345,True)]
            }
            if cat_link in categories:
                for l in categories[cat_link]:
                    id, s = l
                    ret = self.voyo.process_page(id, s, page)
                    rowcnt = int(ret['found_rows'])
                    for it in ret['items']:
                        product_id = it['id']
                        name = it['title']
                        link = it['url']
                        img = it['image']
                        img = img.replace('{WIDTH}x{HEIGHT}', '284x410')
                        vtype = it['type']
                        log('img:{}'.format(img))
                        if vtype == 'show':
                            meta = {}
                            self.list_item(name, link, img, vtype, product_id, action_str, meta)
                        else:
                            info = self.voyo.product_info(product_id)
                            meta = {}
                            img1 = info['content']['image']
                            img1.replace('{WIDTH}x{HEIGHT}', '284x410')
                            plot = info['content']['description']
                            if len(info['content']['genres'])>0:
                                meta['genre'] = info['content']['genres'][0]['title']
                            meta['plot'] = plot
                            if len(info['productionInfo']['originCountries']):
                                meta['country'] = info['productionInfo']['originCountries'][0]
                            meta['rating'] = info['content']['rating']
                            meta['year'] = info['content']['releaseDateLabel']
                            meta['duration'] =  info['content']['length']
                            if 'startAt' in info['stream']:
                                startAt = info['stream']['startAt']
                                self.list_item(f"{name} from {startAt}", link, img, vtype, product_id, action_str, meta)
                            else:
                                play_param = self.voyo.process_play_url(product_id)
                                self.list_play_url(name, link, img, plot, meta, play_param)
                    if rowcnt > page*24:
                        self.list_item('---more---', cat_link, None, None, id, action_str, None, str(page))
            else:
                product_id = params['productId']
                info = self.voyo.product_info(product_id)
                meta = {}
                vtype = info['content']['type']
                if 'seasons' in info['content']:
                    seasons = info['content']['seasons']
                    img = info['content']['image']
                    img = img.replace('{WIDTH}x{HEIGHT}', '284x410')
                    plot = info['content']['description']
                    if len(info['content']['genres']) > 0:
                        meta['genre'] = info['content']['genres'][0]['title']
                    meta['plot'] = plot
                    if len(info['productionInfo']['originCountries'])>0:
                        meta['country'] = info['productionInfo']['originCountries'][0]
                    meta['rating'] = info['content']['rating']
                    meta['year'] = info['content']['releaseDateLabel']
                    meta['duration'] =  info['content']['length']

                    if len(seasons) > 0:
                        for ses in seasons:
                            product_id = ses['id']
                            img = ses['image']
                            img = img.replace('{WIDTH}x{HEIGHT}', '284x410')
                            name = ses['title']
                            link = ses['url']
                            self.list_item(name, link, img, vtype, product_id, action_str, meta)
                else:
                    eposodes = self.voyo.episodes(product_id, page)
                    rowcnt = int(eposodes['found_rows'])
                    for it in eposodes['items']:
                        product_id = it['id']
                        name = it['title']
                        link = it['url']
                        vtype = it['type']
                        img = it['image']
                        img = img.replace('{WIDTH}x{HEIGHT}', '284x410')
                        info = self.voyo.product_info(product_id)
                        meta = {}
                        img1 = info['content']['image']
                        img1.replace('{WIDTH}x{HEIGHT}', '284x410')
                        plot = info['content']['description']
                        if len(info['content']['genres']) >0:
                            meta['genre'] = info['content']['genres'][0]['title']
                        meta['plot'] = plot
                        meta['country'] = info['productionInfo']['originCountries'][0]
                        meta['rating'] = info['content']['rating']
                        meta['year'] = info['content']['releaseDateLabel']
                        meta['duration'] =  info['content']['length']
                        if 'startAt' in info['stream']:
                            startAt = info['stream']['startAt']
                            self.list_item(f"{name} from {startAt}", link, img, vtype, product_id, action_str, meta)
                        else:
                            play_param = self.voyo.process_play_url(product_id)
                            self.list_play_url(name, link, img, plot, meta, play_param)
                    if rowcnt > page*24:
                        self.list_item('---more---', cat_link, None, None, product_id, action_str, None, str(page))


        xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(_handle)

    def device_status(self):
        dialog = xbmcgui.Dialog()
        while not self.voyo.check_device():
            dialog.ok(
            u'Грешка',
            u'Достигнал си максималния брой устройства, които могат да ползваш с този абонамент.',
            u'Моля избери и изтрий устройство, за да продължиш да гледаш.'
            )
            devices = self.voyo.get_devices()
            dev_lst = []
            for name1, name2, act_text, dev_id in devices:
                dev_lst.append('{0} {1} {2} ({3})'.format(name1, name2, act_text, dev_id))
            i = dialog.select(u'Избери устройство за изтриване:', dev_lst)
            if not self.voyo.remove_device(devices[i][3]):
                dialog.ok(u'Грешка', u'Неуспешно изтриване на устройство.')

    def run(self, paramstring):
        log(paramstring)
        params = dict(parse_qsl(paramstring))
        if params:
            if params['action'] == 'listing_sections':
                self.list_content(params)
            elif params['action'] == 'listing_tv':
                self.play_tv(params)
            else:
                raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
        else:
            self.list_categories()

if __name__ == '__main__':
    p = sys.argv[2][1:]
    log(p)
    v = voyo_plugin()
    v.run(p)

