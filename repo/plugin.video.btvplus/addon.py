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


def get_products(url):
    '''
  Get all items from the 'predavaniya' and 'seriali' pages
  Products have no titles, only icons
  '''
    products = []
    url = urllib.parse.urljoin(host, url)
    log("GET " + url, 2)
    ssl._create_default_https_context = ssl._create_unverified_context
    req = urllib.request.Request(url)
    req.add_header('User-agent', user_agent)
    text = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(text, 'html5lib')
    items = soup.find_all(class_='image')

    for item in items:
        title = item.find(class_="title").get_text().rstrip()
        href = urllib.parse.urljoin(host, item.find("a")["href"])
        logoUrl = item.find("img")["src"]
        item = {"title": title, "url": href, "logo": logoUrl}
        products.append(item)

    return products


def get_episodes(url):
    '''
  Get all episodes from the search page
  '''
    episodes = []
    url = urllib.parse.urljoin(host, url)
    log("GET " + url, 2)
    ssl._create_default_https_context = ssl._create_unverified_context
    req = urllib.request.Request(url)
    req.add_header('User-agent', user_agent)
    text = urllib.request.urlopen(req).read().decode('utf-8')
    # log(text, 1)
    soup = BeautifulSoup(text, 'html5lib')
    items = soup.select(".search-item,.episode")
    for item in items:
        try:
            title = item.find(class_="title").get_text().rstrip().lstrip()
            list_item = {"title": title, "url": item.find("a")['href'], "logo": item.find("img")['src']}
            log(list_item, 1)
            episodes.append(list_item)
        except Exception as er:
            log(er, 2)
            continue
    try:
        pages = soup.find_all(class_='page')
        for i in range(0, len(pages)):
            if "current" in pages[i]['class']:
                href = pages[i + 1].a['href']
                item = {"title": next_page_title, "url": href}
                episodes.append(item)
                break
    except Exception as er:
        log("Adding pagination failed %s" % er, 4)

    return episodes


def show_episodes(episodes):
    for episode in episodes:
        if episode['title'] != next_page_title:
            url = make_url({"action": "play_stream", "url": episode["url"], "title": episode["title"]})
            li = xbmcgui.ListItem(episode.get("title"))
            li.setProperty("IsPlayable", 'True')  
            li.setArt({"thumb": episode.get("logo"), "icon":episode.get("logo"), "fanart":episode.get("logo")})
            xbmcplugin.addDirectoryItem(get_addon_handle(), url, li, False)
        else:
            url = make_url({"action": "show_episodes", "url": episode["url"]})
            add_listitem_folder(episode["title"], url)


def get_stream(url):
    url = urllib.parse.urljoin(host, url)
    log("Opening show URL GET " + url, 1)
    ssl._create_default_https_context = ssl._create_unverified_context
    req = urllib.request.Request(url)
    req.add_header("Referer", url)
    req.add_header("User-agent", "Chrome")
    text = urllib.request.urlopen(req).read().decode('utf-8')
    soup = BeautifulSoup(text, 'html5lib')
    item = {"url": None, "logo": None}
    # log(text, 1)
    title = soup.title.get_text()
    # looking for something like this var videoUrl = '/lbin/v3/btvplus/product_player.php?product_id=64874&product_parent_id=54557&type_id=100';
    m = re.compile("var videoUrl = '(.*?)';").findall(text)
    if len(m) > 0:
        player_url = url = urllib.parse.urljoin(host, m[0])
        log("Opening player url " + player_url, 1)
        req = urllib.request.Request(player_url)
        req.add_header("Referer", url)
        req.add_header("User-agent", "Chrome")
        text = urllib.request.urlopen(req).read().decode('utf-8')

        m = re.compile("src\s*:\s*\'(http.+?m3u8)").findall(text)
        if len(m) > 0:
            item["url"] = m[0].replace("\/", "/")
            log("resolved stream: %s" % item["url"], 0)
        else:
            log("No m3u stream found in response: ", 4)
            log(text, 4)
        # m = re.compile('poster[:\s\'"]+(http.*jpg)').findall(text)
        # if len(m) > 0:
        #   item["logo"] = m[0]
        #   if not item["logo"].startswith("http"):
        #     item["logo"] = 'https:'+ item["logo"]
    else:
        log("No streams found!", 4)
        Notification("Грешка", "Видеото не е налично! Вероятно е премахнато от сайта!")
    return item



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
    items = [
        {'title': 'Последни предавания', "url": "search/?type=100", "action": "show_episodes"},
        {'title': 'Предавания', "url": "predavaniya", "action": "show_products"},
        {'title': 'Сериали', "url": "seriali", "action": "show_products"},
        {'title': 'Новини', "url": "search/?type=101", "action": "show_episodes"},
        {'title': 'Спорт', "url": "search/?type=102", "action": "show_episodes"},
        {'title': 'Времето', "url": "search/?type=103", "action": "show_episodes"},
        {'title': 'Търсене', "url": "search", "action": "search"},
    ]

    for item in items:
        url = make_url({"url": item['url'], "action": item['action']})
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
next_page_title = 'Следваща страница'
view_mode = 500

if not action:
    show_categories()

elif action == 'show_products':
    products = get_products(url)
    log("Found %s items" % len(products), 0)

    for product in products:
        url = make_url({"action": "show_episodes", "url": product["url"]})
        add_listitem_folder(product["title"], url, iconImage=product["logo"], thumbnailImage=product["logo"])

elif action == 'show_episodes':
    show_episodes(get_episodes(url))

elif action == 'play_stream':
    stream = get_stream(url)["url"]
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