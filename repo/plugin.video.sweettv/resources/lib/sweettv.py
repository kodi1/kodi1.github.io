# coding: UTF-8
import sys
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime

import routing
import urllib3
import xbmc
import xbmcgui
import xbmcplugin
import xbmcvfs
from six.moves.urllib.parse import urlencode

urllib3.disable_warnings()

from .helper import Helper

base_url = sys.argv[0]
try:
    handle = int(sys.argv[1])
except:
    handle = None  # or whatever you want to do
helper = Helper(base_url, handle)
plugin = routing.Plugin()


def getTime(x, y):
    data = ''
    if y == 'date':
        data = '%Y-%m-%d'
    elif y == 'hour':
        data = '%H:%M'
    return datetime.fromtimestamp(x).strftime(data)


def refreshChannelList():
    if not helper.get_setting('logged'):
        return

    timestamp = int(time.time())
    json_data = {
        'epg_limit_prev': 10,
        'epg_limit_next': 100,
        'epg_current_time': timestamp,
        'need_epg': True,
        'need_list': True,
        'need_categories': True,
        'need_offsets': False,
        'need_hash': False,
        'need_icons': False,
        'need_big_icons': False,
    }

    url = helper.base_api_url.format('TvService/GetChannels.json')
    jsdata = helper.request_sess(url, 'post', headers=helper.headers, data=json_data, json=True, json_data=True,
                                 result=False)

    if jsdata is None:
        return

    jsdata_content = jsdata.content
    jsdata = jsdata.json()

    categories = {}

    if jsdata.get("status", None) == 'OK':
        if "categories" in jsdata:
            for category in jsdata.get('categories', None):
                categories.update({category.get('id', None): category.get('caption', None)})

        if "list" in jsdata:
            xml_root = ET.Element("tv")
            for json_channel in jsdata.get("list"):
                channel = ET.SubElement(xml_root, "channel",
                                        attrib={"id": str(json_channel.get("id")) + ".id.com"})
                ET.SubElement(channel, "display-name", lang=helper.countryCode).text = json_channel.get("name")
                ET.SubElement(channel, "icon", src=json_channel.get("icon_url"))
            for json_channel in jsdata.get("list"):
                if "epg" in json_channel:
                    for json_epg in json_channel.get("epg"):
                        programme_metadata = {
                            "start": time.strftime('%Y%m%d%H%M%S',
                                                   time.localtime(json_epg.get("time_start"))) + " +0100",
                            "stop": time.strftime('%Y%m%d%H%M%S',
                                                  time.localtime(json_epg.get("time_stop") - 1)) + " +0100",
                            "channel": str(json_channel.get("id")) + ".id.com"
                        }

                        if json_channel.get("catchup") and json_channel.get("available") and json_epg.get("available"):
                            catchup = {"catchup-id": str(json_epg.get("id"))}
                            programme_metadata.update(catchup)

                        programme = ET.SubElement(xml_root, "programme", attrib=programme_metadata)
                        if json_epg.get("available") == False and json_channel.get("live_blackout") == True:
                            ET.SubElement(programme, "title",
                                          lang=helper.countryCode).text = "!NOT AVAILABLE! " + json_epg.get(
                                "text")
                        else:
                            ET.SubElement(programme, "title", lang=helper.countryCode).text = json_epg.get("text")
                else:
                    programme = ET.SubElement(xml_root, "programme", attrib={
                        "start": time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())) + " +0100",
                        "stop": time.strftime('%Y%m%d%H%M%S', time.localtime(time.time() + (12 * 60 * 60))) + " +0100",
                        "channel": str(json_channel.get("id")) + ".id.com"})
                    ET.SubElement(programme, "title", lang=helper.countryCode).text = json_channel.get("name")

            tree = ET.ElementTree(xml_root)
            if sys.version_info[:3] >= (3, 9, 0):
                ET.indent(tree, space="  ", level=0)
            xmlstr = '<?xml version="1.0" encoding="utf-8"?>\n'.encode("utf-8") + ET.tostring(xml_root,
                                                                                              encoding='utf-8')
            path_m3u = helper.get_setting('path_m3u')
            file_name = helper.get_setting('name_epg')
            if path_m3u != '' and file_name != '':
                f = xbmcvfs.File(path_m3u + file_name, 'w')
                f.write(xmlstr)
                f.close()

            data = '#EXTM3U\n'
            for json_channel in jsdata.get("list"):
                if json_channel.get('available', None):
                    img = json_channel.get('icon_v2_url', None)
                    cName = json_channel.get('name', None)
                    cid = json_channel.get('id', None)
                    category_list = ''
                    for category in json_channel.get('category', None):
                        if category in categories and category != 1000:
                            category_list += categories[category] + ';'
                    category_list = category_list[:-1]

                    if json_channel.get('catchup', None):
                        catchup = 'catchup="vod" catchup-source="plugin://plugin.video.sweettv/playvid/%s|{catchup-id}"' % (
                            cid)
                    else:
                        catchup = ''
                    data += '#EXTINF:0 tvg-id="%s.id.com" tvg-name="%s" tvg-logo="%s" group-title="%s" %s,%s\nplugin://plugin.video.sweettv/playvid/%s|null\n' % (
                        cid, cName, img, category_list, catchup, cName, cid)

            file_name = helper.get_setting('name_m3u')
            if path_m3u != '' and file_name != '':
                f = xbmcvfs.File(path_m3u + file_name, 'w')
                f.write(data.encode("utf-8"))
                f.close()

            f = xbmcvfs.File(helper.channelListPath, 'wb')
            f.write(jsdata_content)
            f.close()
    else:
        xbmc.log("Failed to update channel list", xbmc.LOGERROR)
        xbmc.log("Failed to update channel list " + str(jsdata), xbmc.LOGDEBUG)

    return jsdata


@plugin.route('/')
def root():
    refresh_token = helper.get_setting('refresh_token')

    xbmc.log("refresh " + refresh_token, xbmc.LOGDEBUG)
    xbmc.log("logged " + str(helper.get_setting('logged')), xbmc.LOGDEBUG)

    if refresh_token == 'None':
        helper.set_setting('bearer', '')
        helper.set_setting('logged', 'false')

    if helper.get_setting('logged'):
        startwt()
    else:
        helper.add_item('[COLOR lightgreen][B]Login[/COLOR][/B]', plugin.url_for(login), folder=False)
        helper.add_item('[B]Settings[/B]', plugin.url_for(settings), folder=False)

    helper.eod()


def initSettings():
    if not helper.uuid:
        import uuid
        uuidx = uuid.uuid4()
        helper.set_setting('uuid', str(uuidx))

    if not helper.mac:
        helper.set_setting('mac', helper.get_random_mac())

    if not helper.access_token_last_update:
        helper.set_setting('access_token_last_update', str(0))

    if not helper.access_token_lifetime:
        helper.set_setting('access_token_lifetime', str(0))

    return


@plugin.route('/startwt')
def startwt():
    helper.add_item('[B]TV[/B]', plugin.url_for(mainpage, mainid='live'), folder=True)
    helper.add_item('[B]Replay[/B]', plugin.url_for(mainpage, mainid='replay'), folder=True)


def refreshToken():
    if not helper.get_setting('logged'):
        return
    # Reduce the token validity to refresh it a bit earlier
    # In this case we always will have a valid Bearer and token
    if int(time.time()) - int(helper.get_setting('access_token_last_update')) > int(int(
            helper.get_setting('access_token_lifetime')) * 0.9):
        json_data = helper.json_data
        json_data.update({"refresh_token": helper.get_setting('refresh_token')})

        jsdata = helper.request_sess(helper.token_url, 'post', headers=helper.headers, data=json_data, json=True,
                                     json_data=True)

        if jsdata is None:
            return

        xbmc.log("refresh " + str(jsdata), xbmc.LOGDEBUG)

        if jsdata.get("access_token", None):
            xbmc.log("Token refresh success", xbmc.LOGDEBUG)
            helper.set_setting('bearer', 'Bearer ' + str(jsdata.get("access_token")))
            helper.headers.update({'authorization': helper.get_setting('bearer')})

            helper.set_setting('access_token_last_update', str(int(time.time())))

            access_token_lifetime = int(jsdata.get("expires_in"))
            helper.set_setting('access_token_lifetime', str(access_token_lifetime))

            return True
        else:
            xbmc.log("Token refresh failed", xbmc.LOGERROR)
            helper.set_setting('logged', 'false')

            return False

    return True


@plugin.route('/getEPG/<epgid>')
def getEPG(epgid):
    epgid, dur = epgid.split('|')
    timestamp = int(time.time())
    json_data = {
        "channels": [
            int(epgid)
        ],
        "epg_current_time": timestamp,
        "need_big_icons": False,
        "need_categories": False,
        "need_epg": True,
        "need_icons": False,
        "need_list": True,
        "need_offsets": False
    }
    url = 'https://api.sweet.tv/TvService/GetChannels.json'
    jsdata = helper.request_sess(url, 'post', headers=helper.headers, data=json_data, json=True, json_data=True)

    if jsdata is None:
        return

    if helper.get_setting('reverse_order') == 'Newest':
        reverse_order = True
    elif helper.get_setting('reverse_order') == 'Oldest':
        reverse_order = False

    tv_shows = []

    if jsdata.get("status", None) == 'OK':
        progs = jsdata['list'][0]['epg']
        for p in progs:
            now = int(time.time())
            tStart = p.get('time_start', None)
            if p['available'] == True and tStart >= now - int(dur) * 24 * 60 * 60 and tStart <= now:
                pid = str(p.get('id', None))
                tit = p.get('text', None)
                date = getTime(p.get('time_start', None), 'date')
                ts = getTime(p.get('time_start', None), 'hour')
                te = getTime(p.get('time_stop', None), 'hour')
                title = '[COLOR=gold]%s[/COLOR] | [B]%s-%s[/B] %s' % (date, ts, te, tit)
                ID = epgid + '|' + pid

                mod = plugin.url_for(playvid, videoid=ID)
                imag = p.get('preview_url_ext', None)
                art = {'icon': imag, 'fanart': helper.addon.getAddonInfo('fanart')}

                info = {'title': title, 'plot': ''}

                tv_show_data = {
                    "title": title,
                    "url": mod,
                    "info": info,
                    "art": art
                }
                tv_shows.append(tv_show_data)

        for s in reversed(tv_shows) if reverse_order is True else tv_shows:
            helper.add_item(s["title"], s["url"], playable=True, info=s["info"], art=s["art"], folder=False,
                            content='videos')

    helper.eod()


@plugin.route('/mainpage/<mainid>')
def mainpage(mainid):
    jsdata = helper.get_channel_list()

    if jsdata.get("status", None) == 'OK':
        for j in jsdata.get('list', []):
            catchup = j.get('catchup', None)
            available = j.get('available', None)
            isShow = False
            if (mainid == 'replay' and catchup and available) or (mainid == 'live' and available):
                isShow = True
            if isShow:
                _id = str(j.get('id', None))
                title = j.get('name', None)
                slug = j.get('slug', None)
                epgs = j.get('epg', None)
                epg = ''
                if mainid == 'live' and epgs:
                    for e in epgs:
                        if e.get('time_stop', None) > int(time.time()):
                            tit = e.get('text', None)
                            ts = getTime(e.get('time_start', None), 'hour')
                            te = getTime(e.get('time_stop', None), 'hour')
                            epg += '[B]%s-%s[/B] %s\n' % (ts, te, tit)

                if mainid == 'live':
                    idx = _id + '|null'  # +slug
                    mod = plugin.url_for(playvid, videoid=idx)
                    fold = False
                    ispla = True
                else:  # id=='replay'
                    dur = str(j.get('catchup_duration', None))
                    idx = _id + '|' + dur
                    mod = plugin.url_for(getEPG, epgid=idx)
                    fold = True
                    ispla = False

                imag = j.get('icon_v2_url', None)
                art = {'icon': imag, 'fanart': helper.addon.getAddonInfo('fanart')}

                info = {'title': title, 'plot': epg}
                helper.add_item('[COLOR gold][B]' + title + '[/COLOR][/B]', mod, playable=ispla, info=info, art=art,
                                folder=fold)

    helper.eod()


@plugin.route('/empty')
def empty():
    return


@plugin.route('/settings')
def settings():
    helper.open_settings()
    helper.refresh()


@plugin.route('/logout')
def logout():
    log_out = helper.dialog_choice('Logout', 'Do you want to log out?', agree='Yes', disagree='No')
    if log_out:
        json_data = {"refresh_token": helper.get_setting('refresh_token')}
        helper.request_sess(helper.logout_url, 'post', headers=helper.headers, data=json_data, json=True,
                            json_data=True)
        helper.set_setting('bearer', '')
        helper.set_setting('logged', 'false')
        helper.refresh()


class QRPopup(xbmcgui.WindowDialog):
    exit_flag = False  # Class-level flag
    running = True

    def __init__(self, auth_code, qrcode_path=None):
        super(QRPopup, self).__init__()

        self.label = xbmcgui.ControlLabel(320, 100, 640, 40, "Enter code {} on the website,".format(auth_code),
                                          alignment=6)
        self.addControl(self.label)

        self.label2 = xbmcgui.ControlLabel(320, 140, 640, 40, "or scan the QR code with your phone!",
                                           alignment=6)
        self.addControl(self.label2)

        if qrcode_path is not None:
            self.qr_image = xbmcgui.ControlImage(490, 180, 300, 300, qrcode_path)
            self.addControl(self.qr_image)

        self.close_button = xbmcgui.ControlButton(540, 500, 200, 50, "Close", alignment=6)
        self.addControl(self.close_button)
        self.setFocus(self.close_button)

        self.monitor_thread = threading.Thread(target=self.monitor_exit_flag)
        self.monitor_thread.setDaemon(True)
        self.monitor_thread.start()

    def onControl(self, control):
        if control == self.close_button:
            QRPopup.running = False
            self.close()

    def monitor_exit_flag(self):
        while QRPopup.running:
            if QRPopup.exit_flag:
                QRPopup.running = False
                self.close()
            time.sleep(0.5)


def show_popup(auth_code, qrcode_path=None):
    QRPopup.exit_flag = False
    window = QRPopup(auth_code, qrcode_path)
    window.doModal()
    del window
    return None


@plugin.route('/login')
def login():
    jsdata = helper.request_sess(helper.auth_url, 'post', headers=helper.headers, data=helper.json_data, json=True,
                                 json_data=True)

    if jsdata is None:
        return

    auth_code = jsdata.get("auth_code")
    if jsdata.get("result") != 'OK' or not auth_code:
        helper.notification('Information', 'Login error')
        helper.set_setting('logged', 'false')
        return

    resp = helper.request_sess("https://api.qrserver.com/v1/create-qr-code/",
                               params={"data": "sweet.tv/addDevice?connectCode={}".format(auth_code)}, result=False)

    path = None
    if resp.status_code == 200:
        try:
            path = xbmcvfs.translatePath('special://temp') + "{}.png".format(auth_code)
        except:
            path = xbmc.translatePath('special://temp') + "{}.png".format(auth_code)
        f = xbmcvfs.File(path, 'w')
        f.write(resp.content)
        f.close()

    def delayed_close():
        # wait for user to enter code
        jsdata = {"auth_code": auth_code}
        from json import dumps
        json_data = dumps(jsdata, separators=(',', ':'))
        result = None
        headers = helper.headers
        headers.update({'Content-Type': 'application/json'})

        while not result:
            if not QRPopup.running:
                helper.notification('Information', 'Login interrupted')
                helper.set_setting('logged', 'false')
                if path is not None:
                    xbmcvfs.delete(path)
                return
            jsdata = helper.request_sess(helper.check_auth_url, 'post', headers=headers, data=json_data, json=True,
                                         json_data=False)

            if jsdata is None:
                return

            xbmc.log("login " + str(jsdata), xbmc.LOGDEBUG)
            if jsdata.get("result") == "COMPLETED":
                result = jsdata
            else:
                time.sleep(3)

        if result.get("result") == 'COMPLETED':

            access_token = result.get("access_token")
            refresh_token = result.get("refresh_token")
            helper.set_setting('bearer', 'Bearer ' + str(access_token))
            helper.set_setting('refresh_token', str(refresh_token))
            helper.set_setting('logged', 'true')
            helper.set_setting('access_token_last_update', str(int(time.time())))

            access_token_lifetime = int(jsdata.get("expires_in"))
            helper.set_setting('access_token_lifetime', str(access_token_lifetime))

            refreshChannelList()
        else:

            info = jsdata.get('result', None)
            helper.notification('Information', info)

            helper.set_setting('logged', 'false')

        QRPopup.exit_flag = True

    t = threading.Thread(target=delayed_close)
    t.setDaemon(True)
    t.start()

    show_popup(auth_code, path)

    if path is not None:
        xbmcvfs.delete(path)

    helper.refresh()


@plugin.route('/playvid/<videoid>')
def playvid(videoid):
    DRM = None
    lic_url = None
    PROTOCOL = 'mpd'
    subs = None

    if not helper.get_setting('logged'):
        xbmcgui.Dialog().notification('Sweet.tv', 'Log in to the plugin', xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(helper.handle, False, xbmcgui.ListItem())
    else:
        idx, pid = videoid.split('|')
        json_data = {
            'without_auth': True,
            'channel_id': int(idx),
            # 'accept_scheme': ['HTTP_HLS',],
            'multistream': True,
        }
        vod = False
        if pid != 'null':
            json_data.update({'epg_id': int(pid)})
            vod = True

        url = helper.base_api_url.format('TvService/OpenStream.json')
        jsdata = helper.request_sess(url, 'post', headers=helper.headers, data=json_data, json=True, json_data=True)

        if jsdata is None:
            return

        if jsdata.get("code", None) == 13:
            xbmcgui.Dialog().notification('Sweet.tv', 'Recording unavailable', xbmcgui.NOTIFICATION_INFO)
            xbmcplugin.setResolvedUrl(helper.handle, False, xbmcgui.ListItem())
        if jsdata.get("result", None) == 'OK':
            host = jsdata.get('http_stream', None).get('host', None).get('address', None)
            nt = jsdata.get('http_stream', None).get('url', None)
            stream_url = 'https://' + host + nt
            if jsdata.get('scheme', None) == 'HTTP_DASH':
                if jsdata.get('drm_type', None) == 'DRM_WIDEVINE':
                    licURL = jsdata.get('license_server', None)
                    hea_lic = {
                        'User-Agent': helper.UA,
                        'origin': 'https://sweet.tv',
                        'referer': 'https://sweet.tv/'
                    }
                    lic_url = '%s|%s|R{SSM}|' % (licURL, urlencode(hea_lic))
                    DRM = 'com.widevine.alpha'
                else:
                    lic_url = None
                    DRM = None
                PROTOCOL = 'mpd'
                subs = None

            elif jsdata.get('scheme', None) == 'HTTP_HLS':
                lic_url = None
                mpdurl = ''
                DRM = None
                PROTOCOL = 'hls'
                subs = None

            if helper.get_setting('playerType') == 'ffmpeg' and DRM is None:
                helper.ffmpeg_player(stream_url)
            else:
                helper.playstream(stream_url, lic_url, PROTOCOL, DRM, flags=False, subs=subs, vod=vod)


@plugin.route('/listM3U')
def listM3U():
    if helper.get_setting('logged'):
        file_name = helper.get_setting('name_m3u')
        path_m3u = helper.get_setting('path_m3u')
        if file_name == '' or path_m3u == '':
            xbmcgui.Dialog().notification('Sweet.tv', 'Specify the file name and destination directory.',
                                          xbmcgui.NOTIFICATION_ERROR)
            return
        xbmcgui.Dialog().notification('Sweet tv', 'Generating M3U list.', xbmcgui.NOTIFICATION_INFO)
        channels = helper.get_channel_list()
        if channels.get("status", None) == 'OK':
            xbmcgui.Dialog().notification('Sweet.tv', 'M3U list generated.', xbmcgui.NOTIFICATION_INFO)
    else:
        xbmcgui.Dialog().notification('Sweet.tv', 'Log in to the plugin.', xbmcgui.NOTIFICATION_INFO)


class SweetTV(Helper):
    def __init__(self):
        super(SweetTV, self).__init__()
        plugin.run()
