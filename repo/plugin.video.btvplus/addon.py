# -*- coding: utf-8 -*-
import os
import re
import time
import base64
import urllib.request, urllib.error, urllib.parse
import xbmcgui
import requests
from bs4 import BeautifulSoup
from kodibgcommon.logging import *
from kodibgcommon.utils import *
from kodibgcommon.notifications import *
import ssl

from page_scraper import PageScraper


def show_episodes(episodes):
    for episode in episodes:
        if episode['title'] != next_page_title:
            url = make_url({"action": "play_stream", "url": episode["path"], "title": episode["title"]})
            li = xbmcgui.ListItem(episode.get("title"))
            li.setProperty("IsPlayable", 'True')
            li.setArt({"thumb": episode.get("logo"), "icon": episode.get("logo"), "fanart": episode.get("logo")})
            xbmcplugin.addDirectoryItem(get_addon_handle(), url, li, False)
        else:
            url = make_url({"action": "show_episodes", "url": episode["path"]})
            add_listitem_folder(episode["title"], url)


def update(name, location, crash=None):
    try:
        lu = settings.last_update
        day = time.strftime("%d")
        if lu == "" or lu != day:
            import ga
            settings.last_update = day
            p = {}
            p['an'] = get_addon_name()
            p['av'] = get_addon_version()
            p['ec'] = 'Addon actions'
            p['ea'] = name
            p['ev'] = '1'
            p['ul'] = get_kodi_language()
            p['cd'] = location
            ga.ga('UA-79422131-4').update(p, crash)
    except:
        pass


def show_categories():
    url = make_url({"url": "https://btvplus.bg/live/", "action": "play_live"})
    add_listitem_unresolved("bTV на живо", url)
    for item in scraper.sections:
        url = make_url({"url": item['path'], "action": item['action']})
        add_listitem_folder(item['title'], url)

    update('browse', 'Categories')


def get_token():
    headers = {
        'User-Agent': user_agent,
        'authority': 'btvplus.bg',
        'accept': 'text/html, application/xhtml+xml, application/xml, application/json, text/plain, */*',
        'dnt': '1',
        'origin': host,
        'Connection': 'keep-alive',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': host,
        'accept-language': 'bg-BG,bg;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip'
    }

    res = requests.get('https://dai-api.bweb.bg:3000/get-token', headers=headers)
    # log(res, 4)
    json_obj = res.json()
    log("Got token: %s" % json_obj['access_token'], 4)
    return json_obj['access_token']


params = get_params()
action = params.get("action")
id = params.get("id")
url = params.get("url")
title = params.get("title")
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
host = "https://btvplus.bg/"
scraper = PageScraper(log, host)
next_page_title = 'Следваща страница'
view_mode = 500

if not action:
    show_categories()

elif action == 'show_products':
    products = scraper.get_items(url)
    log("Found %s items" % len(products), 0)

    for product in products:
        url = make_url({"action": "show_episodes", "url": product["path"]})
        add_listitem_folder(product["title"], url, iconImage=product["logo"], thumbnailImage=product["logo"])

elif action == 'show_episodes':
    show_episodes(scraper.get_items(url))

elif action == 'play_stream':
    stream = scraper.get_stream(url)["url"]
    log('Extracted stream %s ' % stream, 0)
    if stream:
        add_listitem_resolved_url(title, stream)


elif action == 'play_live':
    headers = {
        'User-Agent': user_agent,
        'Accept': '*/*',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Origin': host,
        'Connection': 'keep-alive',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': host,
        'Accept-Language': 'bg-BG,bg;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip',
        'Authorization': 'Bearer ' + get_token()
    }
    payload = {
        'live_config': 'projects/239117298520/locations/europe-west1/liveConfigs/btv-rmt-dai',
        'gam_settings': {
            'stream_id': '951fbecc-7c18-4a8d-b55e-ef84956ab3b1:GRQ'
        }
    }
    res = requests.post(
        'https://videostitcher.googleapis.com/v1/projects/239117298520/locations/europe-west1/liveSessions',
        json=payload, headers=headers)
    json_obj = res.json()
    log("resolved stream: %s" % json_obj['playUri'], 0)
    add_listitem_resolved_url("bTV на живо", json_obj['playUri'])

elif action == 'search':

    keyboard = xbmc.Keyboard('', 'Търсене...')
    keyboard.doModal()
    searchText = ''
    if keyboard.isConfirmed():
        searchText = urllib.parse.quote_plus(keyboard.getText())
        if searchText != '':
            show_episodes(get_episodes('search/?q=%s' % searchText))

xbmcplugin.endOfDirectory(get_addon_handle())
xbmcplugin.setContent(get_addon_handle(), 'movies')
xbmc.executebuiltin("Container.SetViewMode(%s)" % view_mode)
