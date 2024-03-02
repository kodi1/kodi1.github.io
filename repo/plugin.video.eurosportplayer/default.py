
# coding: utf8

import sys
import xbmcgui
import xbmcplugin
import urllib.parse as urllib
import xbmc
import xbmcaddon
import xbmcvfs
#import imp

import json
import datetime

import requests
import importlib

importlib.reload(sys)
#sys.setdefaultencoding('utf8')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse_qs(sys.argv[2][1:])
#xbmcplugin.setContent(addon_handle, 'movies')

_addon_id      = 'plugin.video.eurosportplayer'
_addon         = xbmcaddon.Addon(id=_addon_id)
_addon_name    = _addon.getAddonInfo('name')
__language__   = _addon.getLocalizedString
_addon_handler = int(sys.argv[1])
_addon_url     = sys.argv[0]
_addon_path    = xbmcvfs.translatePath(_addon.getAddonInfo('path') )

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def availableInTerritoryCheck(i,id):
    j = 0
    availableInTerritory = False
    if id == 0:
        while j < len(espplayerMain['included'][i]['attributes']['geoRestrictions']['countries']):
            if espplayerMain['included'][i]['attributes']['geoRestrictions']['countries'][j] == territory \
                    or espplayerMain['included'][i]['attributes']['geoRestrictions']['countries'][j] == 'world':
                availableInTerritory = True
                break
            j = j + 1
    elif id == 1:
        while j < len(espplayerArchiveAuswahl['included'][i]['attributes']['geoRestrictions']['countries']):
            if espplayerArchiveAuswahl['included'][i]['attributes']['geoRestrictions']['countries'][j] == territory \
                    or espplayerArchiveAuswahl['included'][i]['attributes']['geoRestrictions']['countries'][j] == 'world':
                availableInTerritory = True
                break
            j = j + 1
    elif id == 2:
        while j < len(espplayerSchedule['included'][i]['attributes']['geoRestrictions']['countries']):
            if espplayerSchedule['included'][i]['attributes']['geoRestrictions']['countries'][j] == territory \
                    or espplayerSchedule['included'][i]['attributes']['geoRestrictions']['countries'][j] == 'world':
                availableInTerritory = True
                break
            j = j + 1
    return availableInTerritory

def zeitformatierung(time):
    #funktioniert nicht, daher zurückgeändert
    # return datetime.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.datetime(int(time[:4]),
    int(time[
        5:7]), int(
        time[8:10]), int(
        time[11:13]), int(
        time[14:16]), int(
        time[17:19]))

def bildurlherausfinden(i, id):
    j = 0
    if id == 0:
        while j < len(espplayerMain['included']):
            if espplayerMain['included'][j]['id'] == espplayerMain['included'][i]['relationships']['images']['data'][0][
                'id']:
                bildurl = espplayerMain['included'][j]['attributes']['src']
                break
            j = j + 1
    elif id == 1:
        while j < len(espplayerArchiveAuswahl['included']):
            if espplayerArchiveAuswahl['included'][j]['id'] == espplayerArchiveAuswahl['included'][i]['relationships']['images']['data'][0][
                'id']:
                bildurl = espplayerArchiveAuswahl['included'][j]['attributes']['src']
                break
            j = j + 1
    elif id == 2:
        while j < len(espplayerSchedule['included']):
            if espplayerSchedule['included'][j]['id'] == \
                    espplayerSchedule['included'][i]['relationships']['images']['data'][0][
                        'id']:
                bildurl = espplayerSchedule['included'][j]['attributes']['src']
                break
            j = j + 1
    return bildurl

def umrechnungZeitzoneUnterschiedSekunden():
    # Umrechnung Zeitzone
    t = str(datetime.datetime.now() - datetime.datetime.utcnow())
    h, m, s = t.split(':')
    secondsDelta = int(h) * 60 * 60 + int(m) * 60
    # +int (s) ; macht mit Android probleme
    return secondsDelta

def createOrdner(mode, foldername):
    url = build_url(
        {'mode': mode, 'foldername': foldername})
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def createOrdnerwithURL(mode, foldername, url):
    url = build_url(
        {'mode': mode, 'foldername': foldername, 'url': url})
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

mode = args.get('mode', None)

#Rohdaten
addon = xbmcaddon.Addon()
devicePath = addon.getSetting('Device Path')
cookie = addon.getSetting('cookie')

now = datetime.datetime.now()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'
header = {
    'Host': 'eu3-prod-direct.eurosportplayer.com',
    'User-Agent': user_agent,
    'Referer': 'https://www.eurosportplayer.com/',
    'X-disco-client': 'WEB:UNKNOWN:esplayer:prod', # wird benötigt
    'Cookie': cookie, # enter cookie into /resources/settings.xml as default-value at cookie-setting (line 8)
}

territory = 'de'
urlEPG = 'https://eu3-prod-direct.eurosportplayer.com/cms/routes/home?include=default'
urlMe = 'https://eu3-prod-direct.eurosportplayer.com/users/me'
urlStream1 = 'https://eu3-prod-direct.eurosportplayer.com/playback/v2/videoPlaybackInfo/'
urlStream2 = '?usePreAuth=true'
urlArchiveAuswahl = 'https://eu3-prod-direct.eurosportplayer.com/cms/routes/on-demand?include=default'
urlStart = 'https://eu3-prod-direct.eurosportplayer.com/cms/routes'
urlSchedule = 'https://eu3-prod-direct.eurosportplayer.com/cms/routes/schedule?include=default'

if mode is None:
    #Territory herausfinden
    meData = requests.get(url=urlMe, headers=header)
    meData = meData.json()

    try:
        territory = str(meData['data']['attributes']['verifiedHomeTerritory'])
    except:
        try:
            territory = str(meData['data']['attributes']['currentLocationTerritory'])
        except:
            xbmc.log("Fehler: "+str(meData))
            xbmcgui.Dialog().ok(_addon_name, str(meData))
            xbmcplugin.setResolvedUrl(_addon_handler, False, xbmcgui.ListItem())
            sys.exit()

    #Main auslesen:
    espplayerMain = requests.get(url=urlEPG, headers=header)
    espplayerMain = espplayerMain.json()
    i = 0
    i1 = 0
    availableInTerritory = False
    j = 0
    arrayZeitID = []
    ersterListeneintrag = True
    espversion = 0
    while i < len(espplayerMain['included']):
        # print(str(i))
        try:
            if espplayerMain['included'][i]['attributes']['videoType'] == 'LIVE':
                xbmc.log("Try to open ID: "+str(i))
                if availableInTerritoryCheck(i,0):
                    xbmc.log("Territory ok")
                    #espplayerMain['included'][i]['attributes']['scheduleStart']
                    datetime_start = zeitformatierung(espplayerMain['included'][i]['attributes']['availabilityWindows'][0]['playableStart'])
                    xbmc.log("datetime_start: "+str(datetime_start))
                    #5 min vor Streamstart anzeigen
                    #if True:
                    if (datetime.datetime.utcnow() - datetime_start > datetime.timedelta(seconds=-300)):
                        xbmc.log("Starttime ok")
                        eintraghinzugefuegt = False
                        sender = espplayerMain['included'][i]['attributes']['path'].split('/')
                        xbmc.log("Sender: "+str(sender[0]))
                        if str(sender[0][0:11]) == 'eurosport-1':
                            espversion = 1
                        elif str(sender[0][0:11]) == 'eurosport-2' or str(sender[0][0:12]) == 'eurorsport-2':
                            espversion = 2
                        else:
                            espversion = 0

                        if ersterListeneintrag:
                            arrayZeitID.append(datetime_start)
                            arrayZeitID.append(i)
                            arrayZeitID.append(espversion)
                            ersterListeneintrag = False
                            eintraghinzugefuegt = True
                        else:
                            k = 0
                            while k < len(arrayZeitID):
                                if datetime_start < arrayZeitID[k]:
                                    arrayZeitID.insert(k, datetime_start)
                                    arrayZeitID.insert(k+1, i)
                                    arrayZeitID.insert(k+2, espversion)
                                    eintraghinzugefuegt = True
                                    break
                                k = k + 3

                        if eintraghinzugefuegt == False:
                            arrayZeitID.append(datetime_start)
                            arrayZeitID.append(i)
                            arrayZeitID.append(espversion)
        except KeyError:
            i1 = i1 + 1
        i = i + 1

    foldername = __language__(30100) + ':'
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)


    #Eurosport 1
    i = 1
    while i < len(arrayZeitID):
        if arrayZeitID[i+1] == 1:
            datetime_start_local = arrayZeitID[i-1] + datetime.timedelta(seconds=int(umrechnungZeitzoneUnterschiedSekunden()))
            sender = espplayerMain['included'][arrayZeitID[i]]['attributes']['path'].split('/')

            #endzeit
            datetime_ende = zeitformatierung(espplayerMain['included'][arrayZeitID[i]]['attributes']['scheduleEnd'])
            datetime_ende_local = datetime_ende + datetime.timedelta(seconds=umrechnungZeitzoneUnterschiedSekunden())

            try:
                secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
            except KeyError:
                secondaryTitle = ''
            if espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType'] == 'LIVE':
                foldername = str(
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType']+' - '+str(datetime_start_local)[11:16] + ' - ' + str(datetime_ende_local)[11:16] + __language__(30106)+': ' +
                    sender[0] + ': ' + espplayerMain['included'][arrayZeitID[i]]['attributes']['name'] + ': ' +
                    secondaryTitle + ' (' +
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['materialType'] + ')')
            else:
                foldername = str(str(datetime_start_local)[11:16]+' - '+str(datetime_ende_local)[11:16]+ __language__(30106)+': '+
                  sender[0]+': '+espplayerMain['included'][arrayZeitID[i]]['attributes']['name'] +
                                 ': '+secondaryTitle +
                                 ' ('+espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType']+ ') ('
                                 +espplayerMain['included'][arrayZeitID[i]]['attributes']['materialType']+')')
            url = build_url({'mode': 'playStream', 'foldername': foldername, 'streamID': espplayerMain['included'][arrayZeitID[i]]['id']})
            li = xbmcgui.ListItem(foldername)
            li.setArt({'icon': bildurlherausfinden(arrayZeitID[i], 0)})
            li.setProperty('IsPlayable', 'true')
            try:
                secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['description'])
            except KeyError:
                try:
                    secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['name'])+ ' - '+str(espplayerMain['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
                except KeyError:
                    secondaryTitle = ''
            li.setInfo('video', {'plot': str(espplayerMain['included'][arrayZeitID[i]]['attributes']['scheduleStart']+' - '+secondaryTitle)})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        i = i + 3

    #Eurosport 2
    i = 1
    while i < len(arrayZeitID):
        if arrayZeitID[i+1] == 2:
            datetime_start_local = arrayZeitID[i-1] + datetime.timedelta(seconds=int(umrechnungZeitzoneUnterschiedSekunden()))
            sender = espplayerMain['included'][arrayZeitID[i]]['attributes']['path'].split('/')

            #endzeit
            datetime_ende = zeitformatierung(espplayerMain['included'][arrayZeitID[i]]['attributes']['scheduleEnd'])
            datetime_ende_local = datetime_ende + datetime.timedelta(seconds=umrechnungZeitzoneUnterschiedSekunden())
            try:
                secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
            except KeyError:
                secondaryTitle = ''
            if espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType'] == 'LIVE':
                foldername = str(
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType']+' - '+str(datetime_start_local)[11:16] + ' - ' + str(datetime_ende_local)[11:16] + __language__(30106)+': ' +
                    sender[0] + ': ' + espplayerMain['included'][arrayZeitID[i]]['attributes']['name'] + ': ' +
                    secondaryTitle + ' (' +
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['materialType'] + ')')
            else:
                foldername = str(str(datetime_start_local)[11:16]+' - '+str(datetime_ende_local)[11:16]+ __language__(30106)+': '+
                  sender[0]+': '+espplayerMain['included'][arrayZeitID[i]]['attributes']['name'] +': '+secondaryTitle + ' ('+espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType']+ ') ('+espplayerMain['included'][arrayZeitID[i]]['attributes']['materialType']+')')
            url = build_url({'mode': 'playStream', 'foldername': foldername, 'streamID': espplayerMain['included'][arrayZeitID[i]]['id']})
            li = xbmcgui.ListItem(foldername)
            li.setArt({'icon': bildurlherausfinden(arrayZeitID[i],0)})
            li.setProperty('IsPlayable', 'true')
            try:
                secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['description'])
            except KeyError:
                try:
                    secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['name'])+ ' - '+str(espplayerMain['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
                except KeyError:
                    secondaryTitle = ''
            li.setInfo('video', {'plot': str(espplayerMain['included'][arrayZeitID[i]]['attributes']['scheduleStart']+' - '+secondaryTitle)})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        i = i + 3

    foldername = __language__(30101) + ':'
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    #Bonuskanäle
    i = 1
    while i < len(arrayZeitID):
        if arrayZeitID[i+1] == 0:
            datetime_start_local = arrayZeitID[i-1] + datetime.timedelta(seconds=int(umrechnungZeitzoneUnterschiedSekunden()))
            sender = espplayerMain['included'][arrayZeitID[i]]['attributes']['path'].split('/')
            #endzeit
            datetime_ende = zeitformatierung(espplayerMain['included'][arrayZeitID[i]]['attributes']['scheduleEnd'])
            datetime_ende_local = datetime_ende + datetime.timedelta(seconds=umrechnungZeitzoneUnterschiedSekunden())

            if espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType'] == 'LIVE':
                try:
                    secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
                except KeyError:
                    secondaryTitle = ''
                foldername = str(
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType']+' - '+str(datetime_start_local)[11:16] + ' - ' + str(datetime_ende_local)[11:16] + __language__(30106)+': ' +
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['name'] + ': ' +
                    secondaryTitle + ' (' +
                    espplayerMain['included'][arrayZeitID[i]]['attributes']['materialType'] + ')')
            else:
                foldername = str(str(datetime_start_local)[11:16]+' - '+str(datetime_ende_local)[11:16]+ __language__(30106)+': '+
                  espplayerMain['included'][arrayZeitID[i]]['attributes']['name'] +' ('+espplayerMain['included'][arrayZeitID[i]]['attributes']['broadcastType']+ ') ('+espplayerMain['included'][arrayZeitID[i]]['attributes']['materialType']+')')
            url = build_url({'mode': 'playStream', 'foldername': foldername, 'streamID': espplayerMain['included'][arrayZeitID[i]]['id']})
            li = xbmcgui.ListItem(foldername)
            li.setArt({'icon': bildurlherausfinden(arrayZeitID[i],0)})
            li.setProperty('IsPlayable', 'true')
            try:
                secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['description'])
            except KeyError:
                try:
                    secondaryTitle = str(espplayerMain['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
                except KeyError:
                    secondaryTitle = ''
            li.setInfo('video', {'plot': str(espplayerMain['included'][arrayZeitID[i]]['attributes']['scheduleStart']+' - '+secondaryTitle)})
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        i = i + 3

    foldername = '--------------------------------------'
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    createOrdner('Archive', __language__(30102))

    'Schedule:'
    foldername = '--------------------------------------'
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    createOrdner('Schedule', __language__(30103)+' Eurosport 1')
    createOrdner('Schedule', __language__(30103)+' Eurosport 2')

    foldername = '--------------------------------------'
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    foldername = __language__(30104)+':'
    li = xbmcgui.ListItem(foldername)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    espplayerSchedule = requests.get(url=urlSchedule, headers=header)
    espplayerSchedule = espplayerSchedule.json()
    i = 0
    i1 = 0
    availableInTerritory = False
    j = 0
    arrayZeitID = []
    ersterListeneintrag = True
    while i < len(espplayerSchedule['included']):
        # print(str(i))
        try:
            if espplayerSchedule['included'][i]['attributes']['broadcastType'] == 'LIVE':
                if availableInTerritoryCheck(i, 2):
                    datetime_start = zeitformatierung(
                        espplayerSchedule['included'][i]['attributes']['availabilityWindows'][0]['playableStart'])
                    # 5 min vor Streamstart anzeigen
                    if (datetime.datetime.utcnow() - datetime_start < datetime.timedelta(seconds=-299)):
                        eintraghinzugefuegt = False
                        if ersterListeneintrag:
                            arrayZeitID.append(datetime_start)
                            arrayZeitID.append(i)
                            ersterListeneintrag = False
                            eintraghinzugefuegt = True
                        else:
                            k = 0
                            while k < len(arrayZeitID):
                                if datetime_start < arrayZeitID[k]:
                                    arrayZeitID.insert(k, datetime_start)
                                    arrayZeitID.insert(k+1, i)
                                    eintraghinzugefuegt = True
                                    break
                                k = k + 2

                        if eintraghinzugefuegt == False:
                            arrayZeitID.append(datetime_start)
                            arrayZeitID.append(i)

        except KeyError:
            i1 = i1 + 1
        i = i + 1

    i = 1
    while i < len(arrayZeitID):
        datetime_start_local = arrayZeitID[i-1] + datetime.timedelta(
                seconds=int(umrechnungZeitzoneUnterschiedSekunden()))

        sender = espplayerSchedule['included'][arrayZeitID[i]]['attributes']['path'].split('/')

        # endzeit
        datetime_ende = zeitformatierung(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['scheduleEnd'])
        datetime_ende_local = datetime_ende + datetime.timedelta(
            seconds=umrechnungZeitzoneUnterschiedSekunden())
        try:
            secondaryTitle = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
        except KeyError:
            secondaryTitle = ''
        foldername = str(
            str(datetime_start_local)[11:16] + ' - ' + str(datetime_ende_local)[11:16] + __language__(30106)+': ' +
            sender[0] + ': ' + espplayerSchedule['included'][arrayZeitID[i]]['attributes']['name'] + ': ' +
            secondaryTitle + ' (' +
            espplayerSchedule['included'][arrayZeitID[i]]['attributes']['materialType'] + ')')

        url = build_url({'mode': 'playStream', 'foldername': foldername,
                         'streamID': espplayerSchedule['included'][arrayZeitID[i]]['id']})
        li = xbmcgui.ListItem(foldername)
        li.setArt({'icon': bildurlherausfinden(arrayZeitID[i], 2)})
        li.setProperty('IsPlayable', 'true')
        try:
            secondaryTitle = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['description'])
        except KeyError:
            try:
                secondaryTitle = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
            except KeyError:
                secondaryTitle = ''

        li.setInfo('video', {'plot': str(
            espplayerSchedule['included'][arrayZeitID[i]]['attributes']['scheduleStart'] + ' - ' + secondaryTitle)})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        i = i + 2


    xbmcplugin.endOfDirectory(addon_handle)

    #except:
    #    xbmcgui.Dialog().ok(_addon_name, str(meData))
    #    xbmcplugin.setResolvedUrl(_addon_handler, False, xbmcgui.ListItem())

elif mode[0] == 'Schedule':

    if args['foldername'][0] == __language__(30103)+' Eurosport 1':
        suchsender = 'eurosport-1'
        suchsender2 = 'eurosport-1'
        foldername = __language__(30103)+' Eurosport 1 ('+__language__(30105)+'):'
        li = xbmcgui.ListItem(foldername)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    elif args['foldername'][0] == __language__(30103)+' Eurosport 2':
        suchsender = 'eurosport-2'
        suchsender2 = 'eurorsport-2'
        foldername =__language__(30103)+' Eurosport 2 ('+__language__(30105)+'):'
        li = xbmcgui.ListItem(foldername)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)
    else:
        suchsender = ''
        suchsender2 = ''
        foldername = 'Error'
        li = xbmcgui.ListItem(foldername)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url='', listitem=li)

    espplayerSchedule = requests.get(url=urlSchedule, headers=header)
    espplayerSchedule = espplayerSchedule.json()
    i = 0
    i1 = 0
    availableInTerritory = False
    j = 0
    arrayZeitID = []
    ersterListeneintrag = True
    while i < len(espplayerSchedule['included']):
        try:
            sender = espplayerSchedule['included'][i]['attributes']['path'].split('/')
            if sender[0][0:len(suchsender)] == suchsender or sender[0][0:len(suchsender2)] == suchsender2:
                if availableInTerritoryCheck(i, 2):
                    datetime_start = zeitformatierung(
                        espplayerSchedule['included'][i]['attributes']['availabilityWindows'][0]['playableStart'])
                    # 5 min vor Streamstart anzeigen
                    if (datetime.datetime.utcnow() - datetime_start < datetime.timedelta(seconds=-299)):
                        eintraghinzugefuegt = False
                        if ersterListeneintrag:
                            arrayZeitID.append(datetime_start)
                            arrayZeitID.append(i)
                            ersterListeneintrag = False
                            eintraghinzugefuegt = True
                        else:
                            k = 0
                            while k < len(arrayZeitID):
                                if datetime_start < arrayZeitID[k]:
                                    arrayZeitID.insert(k, datetime_start)
                                    arrayZeitID.insert(k + 1, i)
                                    eintraghinzugefuegt = True
                                    break
                                k = k + 2

                        if eintraghinzugefuegt == False:
                            arrayZeitID.append(datetime_start)
                            arrayZeitID.append(i)

        except KeyError:
            i1 = i1 + 1
        i = i + 1

    i = 1
    while i < len(arrayZeitID):

        datetime_start_local = arrayZeitID[i - 1] + datetime.timedelta(
            seconds=int(umrechnungZeitzoneUnterschiedSekunden()))

        sender = espplayerSchedule['included'][arrayZeitID[i]]['attributes']['path'].split('/')

        # endzeit
        datetime_ende = zeitformatierung(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['scheduleEnd'])
        datetime_ende_local = datetime_ende + datetime.timedelta(
            seconds=umrechnungZeitzoneUnterschiedSekunden())

        #str(datetime_start_local)[8:10]+'.'+str(datetime_start_local)[5:7]+'.'+str(datetime_start_local)[0:4]
        try:
            secondaryTitle = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
        except KeyError:
            secondaryTitle = ''
        if espplayerSchedule['included'][arrayZeitID[i]]['attributes']['broadcastType'] == 'LIVE':
            foldername = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['broadcastType'])+': '+str(str(datetime_start_local)[11:16] + ' - ' + str(datetime_ende_local)[11:16] + __language__(30106)+': ' +espplayerSchedule['included'][arrayZeitID[i]]['attributes']['name'] + ': '+secondaryTitle+ ' ('+sender[0] + ')')
        else:
            foldername = str(str(datetime_start_local)[11:16] + ' - ' + str(datetime_ende_local)[11:16] + __language__(30106)+': ' +espplayerSchedule['included'][arrayZeitID[i]]['attributes']['name'] + ': '+secondaryTitle+' ('+sender[0] + ')')

        url = build_url({'mode': 'playStream', 'foldername': foldername,
                         'streamID': espplayerSchedule['included'][arrayZeitID[i]]['id']})
        li = xbmcgui.ListItem(foldername)
        li.setArt({'icon': bildurlherausfinden(arrayZeitID[i], 2)})
        li.setProperty('IsPlayable', 'true')
        try:
            secondaryTitle = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['description'])
        except KeyError:
            try:
                secondaryTitle = str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['name'])+' - '+str(espplayerSchedule['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
            except KeyError:
                secondaryTitle = ''
        li.setInfo('video', {'plot': str(
            espplayerSchedule['included'][arrayZeitID[i]]['attributes']['scheduleStart'] + ' - ' +
            secondaryTitle)})

        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        i = i + 2
    xbmcplugin.endOfDirectory(addon_handle)


elif mode[0] == 'Archive':
    archiveAuswahl = requests.get(url=urlArchiveAuswahl, headers=header)
    archiveAuswahl = archiveAuswahl.json()
    i = 0
    i1 = 0
    while i < len(archiveAuswahl['included']):
        name = ''
        try:
            if archiveAuswahl['included'][i]['type'] == 'route':
                if archiveAuswahl['included'][i]['attributes']['url'][:7] == '/sport/':
                    #Beschriftund herausfinden (geht noch nicht)
                    j = 0
                    while j < len(archiveAuswahl['included']):
                        if archiveAuswahl['included'][j]['id'] == \
                                archiveAuswahl['included'][i]['id']:
                            if not(i == j):
                                name = archiveAuswahl['included'][j]['attributes']['name']
                                break
                        j = j + 1

                    if name == '':
                        createOrdnerwithURL('archiveAuswahl', archiveAuswahl['included'][i]['attributes']['url'], archiveAuswahl['included'][i]['attributes']['url'])
                    else:
                        createOrdnerwithURL('archiveAuswahl',name, archiveAuswahl['included'][i]['attributes']['url'])
        except KeyError:
            i1 = i1 + 1
        i = i + 1
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'archiveAuswahl':

 #Main auslesen:
    #urlStart+str(args['url'][0])+'?include=default'
    espplayerArchiveAuswahl = requests.get(url=urlStart+str(args['url'][0])+'?include=default', headers=header)
    espplayerArchiveAuswahl = espplayerArchiveAuswahl.json()
    i = 0
    i1 = 0
    availableInTerritory = False
    j = 0
    arrayZeitID = []
    ersterListeneintrag = True

    while i < len(espplayerArchiveAuswahl['included']):
        try:
            if espplayerArchiveAuswahl['included'][i]['attributes']['videoType'] == 'STANDALONE':
                if availableInTerritoryCheck(i, 1):
                    datetime_start = espplayerArchiveAuswahl['included'][i]['attributes']['scheduleStart']
                    eintraghinzugefuegt = False
                    if ersterListeneintrag:
                        arrayZeitID.append(datetime_start)
                        arrayZeitID.append(i)
                        ersterListeneintrag = False
                        eintraghinzugefuegt = True
                    else:
                        k = 0
                        while k < len(arrayZeitID):
                            if datetime_start < arrayZeitID[k]:
                                arrayZeitID.insert(k, datetime_start)
                                arrayZeitID.insert(k + 1, i)
                                eintraghinzugefuegt = True
                                break
                            k = k + 2

                    if eintraghinzugefuegt == False:
                        arrayZeitID.append(datetime_start)
                        arrayZeitID.append(i)
        except KeyError:
            i1 = i1 + 1
        i = i + 1

    i = 1
    while i < len(arrayZeitID):
        #espplayerMain['included'][i]['attributes']['scheduleStart']
                #+' ('+espplayerArchiveAuswahl['included'][i]['attributes']['broadcastType']+ ') ('+espplayerArchiveAuswahl['included'][i]['attributes']['materialType']+')'
        try:
            secondaryTitle = str(espplayerArchiveAuswahl['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
        except KeyError:
            secondaryTitle = ''

        foldername = str(espplayerArchiveAuswahl['included'][arrayZeitID[i]]['attributes']['scheduleStart']+': '+espplayerArchiveAuswahl['included'][arrayZeitID[i]]['attributes']['name']+' - '+secondaryTitle)
        url = build_url({'mode': 'playStream', 'foldername': foldername, 'streamID': espplayerArchiveAuswahl['included'][arrayZeitID[i]]['id']})
        li = xbmcgui.ListItem(foldername)
        li.setArt({'icon': bildurlherausfinden(arrayZeitID[i], 1)})
        li.setProperty('IsPlayable', 'true')
        try:
            secondaryTitle = str(espplayerArchiveAuswahl['included'][arrayZeitID[i]]['attributes']['secondaryTitle'])
        except KeyError:
            secondaryTitle = ''
        li.setInfo('video', {'plot': str(espplayerArchiveAuswahl['included'][arrayZeitID[i]]['attributes']['scheduleStart']+' - '+secondaryTitle)})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
        i = i + 2
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'playStream':
    urlStream = urlStream1 + args['streamID'][0] + urlStream2
    xbmc.log("urlStream: "+str(urlStream))
    espplayerStream = requests.get(url=urlStream, headers=header)
    if espplayerStream.status_code == 403:
        xbmcgui.Dialog().ok(_addon_name, __language__(30107))
        xbmcplugin.setResolvedUrl(_addon_handler, False, xbmcgui.ListItem())
    else:
        espplayerStream = espplayerStream.json()
        xbmc.log(str(espplayerStream))
        if _addon.getSetting('streamselection') == 'mss':
            streamURL = str(espplayerStream['data']['attributes']['streaming']['mss']['url'])
        elif _addon.getSetting('streamselection') == 'hls':
            streamURL = str(espplayerStream['data']['attributes']['streaming']['hls']['url'])
        elif _addon.getSetting('streamselection') == 'dash':
            streamURL = str(espplayerStream['data']['attributes']['streaming']['dash']['url'])
        else:
            xbmcgui.Dialog().ok(_addon_name, __language__(30108))
            xbmcplugin.setResolvedUrl(_addon_handler, False, xbmcgui.ListItem())
        xbmc.log("StreamURL: "+str(streamURL))
        li = xbmcgui.ListItem(path=streamURL)
        li.setMimeType('application/x-mpegURL')
        li.setProperty('inputstream', 'inputstream.adaptive')
        #li.setProperty('inputstream.adaptive.license_key', "https://discovery-eur.conax.cloud/fairplay/clearkey")
        if _addon.getSetting('streamselection') == 'mss':
            li.setProperty('inputstream.adaptive.manifest_type', 'ism')
        elif _addon.getSetting('streamselection') == 'hls':
            li.setProperty('inputstream.adaptive.manifest_type', 'hls')
        elif _addon.getSetting('streamselection') == 'dash':
            li.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        li.setContentLookup(False)
        xbmcplugin.setResolvedUrl(_addon_handler, True, listitem=li)