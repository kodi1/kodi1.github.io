# -*- coding: utf-8 -*-
#
#     Copyright (C) 2018 zinobg [at] gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

from re import compile
from xbmcvfs import translatePath
import urllib, datetime, json
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import weblogin

# fill in the credentials
if not xbmcaddon.Addon().getSetting('username') or not xbmcaddon.Addon().getSetting('password') or not xbmcaddon.Addon():
    xbmcaddon.Addon().openSettings()

# icons
vid_icon = translatePath(xbmcaddon.Addon().getAddonInfo('path')+"/resources/png/vid_icon.png")
prog_icon = translatePath(xbmcaddon.Addon().getAddonInfo('path')+"/resources/png/prog_icon.png")

# settings
username = xbmcaddon.Addon().getSetting('username')
password = xbmcaddon.Addon().getSetting('password')
quality = xbmcaddon.Addon().getSetting('quality')
timezone = xbmcaddon.Addon().getSetting('index_tz')
hide_babytv = xbmcaddon.Addon().getSetting('hide_babytv')

# URL details
BASE = "http://www.bgtv-on.com/"
subscribe_url = BASE+'subscribe'
recording_url = BASE+'recording'
programme_url = BASE+'programme'
login_url = BASE+'login'
cookie_file = 'cookies_bgtv-on.lwp'

def time_convert(time_orig):
    h, m = time_orig.split(':')
    time_orig = datetime.time(int(h), int(m))
    time_diff = abs(int(timezone)-13)
    if int(timezone) > 13:
        hol = (datetime.datetime.combine(datetime.date(1900, 1, 1), time_orig)+datetime.timedelta(hours=time_diff)).time()
    elif int(timezone)<13:
        hol = (datetime.datetime.combine(datetime.date(1900, 1, 1), time_orig)-datetime.timedelta(hours=time_diff)).time()
    h, m, s = str(hol).split(':')
    time_modified = h+':'+m
    return time_modified


def check_validity(account_active=False):
    cookiepath = weblogin.doLogin(username, password, login_url, cookie_file)
    subscribe_source = weblogin.openUrl(subscribe_url, cookiepath)
    match = compile('<p><span.*>(.+?)<\/span><\/p>').findall(subscribe_source)
    for subs_text in match:
        account_active = True
        dates_match = compile('.* (.+?)-(.+?)-(.+?)\.').findall(subs_text)
        for s_day, s_month, s_year in dates_match:
            date_expire = datetime.datetime(int(s_year), int(s_month), int(s_day))
            date_today = datetime.datetime.now()
            days_delta = date_expire-date_today
            xbmc.log("Account is active! You have "+str(days_delta.days)+" days until it expires")
            if days_delta.days <= 5:
                xbmcgui.Dialog().notification('[ Your subscribtion will expire soon ]', 'Only '+str(days_delta.days)+' days left!', xbmcgui.NOTIFICATION_INFO, 10000, sound=False)
    return (account_active, cookiepath)

def correct_stream_url(raw_stream):
    stream = raw_stream.lstrip('[').rstrip(']').strip('"')
    titles = compile('\/(.+?).stream').findall(stream)
    if not titles:
        titles = compile('\/(.+?).smil').findall(stream)
    for title in titles:
        title = "["+title.replace('_', '] [').upper()+"]"
    return (title, stream)

def LIST_CHANNELS():
    account_active = check_validity()
    source = weblogin.openUrl(BASE+'teko/onairclap.php', account_active[1])
    json_load = json.loads(source)
    for i in range(len(json_load)):
        c_name = ' '.join(json_load[i]['name'].split()).encode('utf-8')
        c_cid = json_load[i]['cid']
        if c_cid == '47' and hide_babytv == 'true':
            continue
        c_logo = json_load[i]['logo']
        name = ('[' + str(int(json_load[i]['percent'])) + '%] ' + c_name.decode())
        addDir(name, c_cid, 21, c_logo)
    if not account_active[0]:
        xbmcgui.Dialog().notification('[ You don\'t have a valide subscription ]', 'Only free TV channels are available', xbmcgui.NOTIFICATION_WARNING, 10000, sound=True)
        xbmc.log("You don't have a valid account, so you are going to watch the free TVs only.")
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def INDEX_CHANNELS(cid):
    url = (BASE + "teko/getchaclap_mbr.php?cid=" + cid)
    cookiepath = weblogin.doLogin(username, password, login_url, cookie_file)
    try:
        source = weblogin.openUrl(url, cookiepath)
        xbmc.log(source)
    except:
        xbmcgui.Dialog().notification('[ You don\'t have premissions to watch this TV channel ]', 'You probably have to pay additionally in order to watch this TV channel.', xbmcgui.NOTIFICATION_WARNING, 10000, sound=True)
    #xbmc.log(str(type(source)))
    src_list = list(source.split(","))
    if quality == 'moderate':
        for i in range(len(src_list)):
            play_list = correct_stream_url(src_list[i])
            addLink('PLAY: '+play_list[0], play_list[1], vid_icon)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    else:
        # Presuming that the first stream has the lowest quality and the last - the highest
        # index 0 : getting the stream link with the lowest quality
        # index -1 : getting the stream link with the highest quality
        if quality == 'low' or len(src_list) == 1:
            element = 0
        if quality == 'high' and len(src_list) > 1:
            element = -1
        xbmc.log('2-quality: '+quality+' and number of streams: '+str(len(src_list)))
        play_list = correct_stream_url(src_list[element])
        # xbmc.log(play_list)
        # loading json clap conf
        source_clap = weblogin.openUrl(BASE+'teko/onairclap.php', cookiepath)
        clap_json_config = json.loads(source_clap)
        for i in range(len(clap_json_config)):
            if clap_json_config[i]['cid'] == cid:
                text_t1 = clap_json_config[i]['chName']
                text_t2 = clap_json_config[i]['name']
                icon = clap_json_config[i]['logo']
        # playing the stream
        liz = xbmcgui.ListItem(play_list[0])
        liz.setInfo(type="Video", infoLabels={"Title": text_t1 + ' :: ' + text_t2})
        liz.setProperty('IsPlayable', 'true')
        xbmc.Player().play(item=play_list[1], listitem=liz)
        xbmcgui.Dialog().notification(text_t1, text_t2, icon, 10000, sound=False)

def LIST_REC():
    cookiepath = weblogin.doLogin(username, password, login_url, cookie_file)
    source = weblogin.openUrl(recording_url, cookiepath)
    match = compile('<a href=recording(.+?)#..class=tab.>(.+?)<\/a>').findall(source)
    for lr_cid, lr_name in match:
        rec_url = (recording_url+lr_cid)
        addDir(lr_name, rec_url, 31, vid_icon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def LIST_REC_CHAN(url):
    cookiepath = weblogin.doLogin(username, password, login_url, cookie_file)
    source = weblogin.openUrl(url, cookiepath)
    match = compile('(<div class="day">(.+?)<\/div>)*(<a href=(.+?)><li><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for useless1, day, useless2, rec_url, time, lrc_name in match:
        if day:
            addDir('=['+day+']=', '', 33, '')
        time_convd = time_convert(time)
        desc_txt = ('['+time_convd+'] '+lrc_name)
        addDir(desc_txt, rec_url.strip('"'), 32, vid_icon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def PLAY_REC_CHAN(cid, name):
    url = (BASE+cid)
    account_active = check_validity()
    if not account_active[0]:
        xbmcgui.Dialog().notification('[ You don\'t have valid subscription ]', 'Not Available without subscription!', xbmcgui.NOTIFICATION_WARNING, 10000, sound=True)
        raise SystemExit
    source_rec = weblogin.openUrl(url, account_active[1])
    match_rec = compile('source:."(.+?)"').findall(source_rec)
    for rec_url in match_rec:
        addLink('PLAY: '+name, rec_url, vid_icon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def INDEX_PROG_CH():
    cookiepath = weblogin.doLogin(username, password, login_url, cookie_file)
    source = weblogin.openUrl(programme_url, cookiepath)
    match = compile('<a href=programme\?cid=(.+?)#..class=tab >(.+?)<\/a>').findall(source)
    for ip_cid, ip_name in match:
        addDir(ip_name, ip_cid, 41, prog_icon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def LIST_PROG_CH(cid):
    url = programme_url+'?cid='+cid
    cookiepath = weblogin.doLogin(username, password, login_url, cookie_file)
    source = weblogin.openUrl(url,cookiepath)
    match = compile('(<div class="day">(.+?)<\/div>)*(<li style="list-style: none;"><span class="time">(.+?)<\/span><span class="title">(.+?)<\/span>)').findall(source)
    for temp1, day, temp2, time, name in match:
        del temp1, temp2
        if day != '':
            addDir('=['+day+']=', cid, 42, prog_icon)
        time_convd = time_convert(time)
        desc_txt = ('['+time_convd+'] '+name)
        addDir(desc_txt, cid, 42, prog_icon)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1]=='/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def addLink(name, url, iconimage):
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': 'DefaultFolder.png', 'thumb': iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)


def addDir(name, cid, mode, iconimage):
    u = sys.argv[0]+"?cid="+urllib.parse.quote_plus(cid)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)
    liz = xbmcgui.ListItem(name)
    liz.setArt({'icon': 'DefaultFolder.png', 'thumb': iconimage})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

####
params = get_params()
cid = None
name = None
mode = None

try:
    cid = urllib.parse.unquote_plus(params["cid"])
except:
    pass
try:
    name = urllib.parse.unquote_plus(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

xbmc.log("Mode: "+str(mode))
xbmc.log("CID: "+str(cid))
xbmc.log("Name: "+str(name))

if len(params) == 0:
    menu_index = xbmcgui.Dialog().contextmenu(['НА ЖИВО', 'НА ЗАПИС', 'ПРОГРАМАТА'])
    if menu_index == 0:
        xbmc.log('Selected from menu: onair')
        LIST_CHANNELS()
    elif menu_index == 1:
        xbmc.log('Selected from menu: recording')
        LIST_REC()
    elif menu_index == 2:
        xbmc.log('Selected from menu: programme')
        INDEX_PROG_CH()
    xbmcplugin.endOfDirectory(int(sys.argv[1]), succeeded=True)

elif mode == 21:
    INDEX_CHANNELS(cid)
elif mode == 31:
    LIST_REC_CHAN(cid)
elif mode == 32:
    PLAY_REC_CHAN(cid, name)
elif mode == 41:
    LIST_PROG_CH(cid)
elif mode == 42:
    INDEX_CHANNELS(cid)
