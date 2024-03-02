# -*- coding: utf-8 -*-
import os
import io
import sys
import json
import time
import xbmc
import base64
import urllib
import xbmcgui
import pickle
import requests
from datetime import datetime, timedelta
from collections import OrderedDict
from kodibgcommon.utils import *
#
# reload(sys)
# sys.setdefaultencoding('utf8')

profile_dir   = get_profile_dir()
cookie_file   = os.path.join(profile_dir, '.cookies')
channels_file = os.path.join(profile_dir, '.channels')
programs_file = os.path.join(profile_dir, '.programs')
response_file = os.path.join(profile_dir, 'last_response.txt')
playlist_file = os.path.join(profile_dir, 'playlist.raw.m3u')
mapping_file  = os.path.join(get_resources_dir(), "map.json")
pua           = base64.b64decode("fFVzZXItQWdlbnQ9RXhvUGxheWVyRGVtby8yLjAuMTMgKExpbnV4LEFuZHJvaWQgNy4wKSBFeG9QbGF5ZXJMaWIvMS41Ljg=")

def save_cookies(s):
  with open(cookie_file, 'w') as f:
    f.truncate()
    pickle.dump(s.cookies._cookies, f)
  return True

def load_cookies():
  jar = requests.cookies.RequestsCookieJar()
  if os.path.isfile(cookie_file):
    with open(cookie_file) as f:
      cookies = pickle.load(f)
      if cookies:
        jar._cookies = cookies
        return jar
  return jar
  
def __request(url, payload=None):
  headers = {'User-Agent': 'okhttp/2.5.0', 'USER_AGENT': 'android'}
  # headers = {'Content-Type': 'application/json; charset=utf-8'}
  method = "POST" if payload else "GET"
  log("**************************************************")
  log("%s %s" % (method, url))
  for key,val in headers.items():
    log("%s: %s" % (key, val))
  if payload:
    res = session.post(url, json=payload, headers=headers)
    ## Obfuscate password in logs
    _pass = payload.get("password")
    if _pass:
      payload["password"] = "********"
    log("%s" % json.dumps(payload))
  else:
    res = session.get(url, headers=headers)
  if settings.debug:
    with open(response_file, "w") as w:
      w.write(res.text)
  return res
  
def login():
  '''
  Login function
  Returns None on successful login. Otherwise it returns an error message.
  '''
  try:
    url =  base64.b64decode("aHR0cDovL3R2Z28udml2YWNvbS5iZy9FUEcvSlNPTi9Mb2dpbj9Vc2VySUQ9")
    res = requests.get(url)
    log("Response: " + res.text)
    settings.url = res.json()["epgurl"]
    settings.epghttpsurl = res.json()["epghttpsurl"]
    settings.enctytoken = res.json()["enctytoken"]
    update("Init", "Categories")
    
    url = get_url(base64.b64decode("Vml2YWNvbVNTT0F1dGg="))
    post_data = {"password": settings.password, "userName": settings.username}
    res = __request(url, post_data)
    log(res.text)
    msg = "Неочаквана грешка. Моля проверете лога"
    
    if res.json().get("retcode") and res.json()["retcode"] != "0":
      if res.json().get("retmsgBG"):
        msg = res.json()["retmsgBG"]
      elif res.json().get("retmsg"):
        msg = res.json()["retmsg"]
      elif res.json().get("desc"):
        msg = res.json()["desc"]      
      return msg

    vivacomSubscribers = res.json()["vivacomSubscribers"] 
    firstActiveSubscription = None
    account = str(settings.account or "default")
    log(" account: " + account)
    
    for sub in vivacomSubscribers:
      if sub["subscriberStatus"] == "active":
        log("Active subscription " + sub["subscriberId"] + " account: " + account)
        firstActiveSubscription = sub
        if (account == "default" or sub["subscriberId"] == account):
          break
        
    if (firstActiveSubscription == None):
      return "Не е намерен активен абонамент"

    settings.checksum = firstActiveSubscription["checksum"]
    settings.subscriberId = firstActiveSubscription["subscriberId"]

    post_data = {"checksum":settings.checksum,"mac":settings.guid,"subscriberId":settings.subscriberId,"terminaltype":"NoCAAndroidPad","userName":settings.username}
    res = __request(url, post_data)

    if(res.json()["retmsg"] != "success"):
      log("Error: " + res.json()["retmsg"])
      return res.json()["retmsg"];
    
    settings.subscriberPassword = res.json()["users"][0]["password"]
    
    save_cookies(session)
    return False
    
  except:
    log_last_exception()
    return msg

def is_cache_older_than(hours=24):
  try:
    from datetime import datetime, timedelta
    treshold = datetime.now() - timedelta(hours=hours)
    modified = datetime.fromtimestamp(os.path.getmtime(channels_file))
    if modified < treshold: #file is older than "hours"
      return True
  except Exception as er:
    log(er)
  return False
  
def get_map():
  map = {}
  log("Using map file: %s" % mapping_file, 2)
  try:
    with io.open(mapping_file, encoding='utf-8') as f:
      map = json.load(f)
    log("map loaded with %s entries" % len(map), 2)
  except Exception as er:
    log(er, 4)
  return map
  
def get_channels():
  progress_bar = None
  channels = {}
  
  try:
    # Try login 2 times before giving up
    errors = login()
    if errors:
      notify_error(errors)
      settings.open()
      errors = login()
      if errors:
        notify_error(errors)
        settings.open()
        return []

    post_data = {"id": settings.subscriberId, "password": settings.subscriberPassword}
    res = __request(get_url(base64.b64decode("U3dpdGNoUHJvZmlsZQ==")), post_data) #SwitchProfile
    
    if settings.debug:
      with open(response_file, "w") as w:
        w.write(res.text)     
    
    if settings.rebuild_cache or not os.path.isfile(channels_file) or is_cache_older_than(settings.refresh_interval):
      progress_bar = xbmcgui.DialogProgressBG()
      progress_bar.create(heading="Канали")
      progress_bar.update(5, "Изграждане на списък с канали...")
      res = __request(get_url(base64.b64decode("QWxsQ2hhbm5lbA==")), post_data) #AllChannel
      
      if res.json().get("channellist"):
        pl = "#EXTM3U\n"
        progress_bar.update(50, "Getting channels...")
        settings.rebuild_cache = False
        i = 0
        p = 50
        map = get_map()
        
        for item in res.json()["channellist"]:
          p += 5
          progress_bar.update(p, "Изграждане на списък с канали...")
          
          if item.get("issubscribed") == "1":
            channel = {}
            i += 1
            channel["name"] = item["name"]
            channel["order"] = i
            channel["mediaid"] = item["mediaid"]
            channel["logo"] = item.get("logo").get("url")
            channels[item["id"]] = channel
            ### move this out of the issubscribed check to retrieve all channels
            ua = pua if settings.append_ua else ""
            log(item["name"].decode("utf-8"), 2)
            playurl = item.get("playurl")
            if playurl:
              if "|" in playurl:
                playurl = playurl.split("|")[0]
                
            pl += "#EXTINF:-1 radio=\"false\" tvg-logo=\"%s\" tvg-id=\"%s\",%s\n%s%s\n" % (item.get("logo").get("url"), map.get(item["name"].decode("utf-8"),item["name"].decode("utf-8")), item["name"], playurl, ua)
          
        with open(channels_file, "w") as w:
          w.write(json.dumps(channels, ensure_ascii=False))      

        with open(playlist_file, "w") as w:
          w.write(pl)
          
      else:
        # Rebuild cache during next run
        settings.rebuild_cache = True  
    else: 
      #load channels from cache
      channels = json.load(open(channels_file))
    
    if len(channels) > 0:
      channels = OrderedDict(sorted(channels.iteritems(), key=lambda c: c[1]['order'], reverse=False))
      log("%s channels found" % len(channels))
    else:
      log("No channels found!", 4)
  except:
    log_last_exception()
    
  if progress_bar:
    progress_bar.close()
    
  return channels

def get_channel(id):
  try:
    channels = json.load(open(channels_file))
    log("Getting channel with id %s" % id)

    channel = channels.get(id)
    
    if channel:
      streams = get_stream(id, channel["mediaid"], 2, "VIDEO_CHANNEL")

      playpaths = []
      try: 
        playpaths = streams.split("|")
      except:
        try: 
          playpaths[0] = streams
        except: 
          log("No playpath found for channel %s" % channel["name"], 4)
      channel["playpaths"] = playpaths
      
      #EPG
      try:
        now = datetime.now()
        begintime = now.strftime("%Y%m%d%H%M%S")
        post_data = {"begintime": begintime, "channelid":id, "count": 1, "offset":0, "type":2}
        res = __request(get_url("PlayBillList"), post_data)
        __json = res.json().get("playbilllist")[0]
        
        channel["desc"] = ""
        
        start = "%s:%s" % (__json["starttime"][8:10], __json["starttime"][11:13])
        end = "%s:%s" % (__json["endtime"][8:10], __json["endtime"][11:13])
        
        if start:
          channel["desc"] += " %s" % start
        if end:
          channel["desc"] += " - %s" % end
          
        channel["desc"] += " %s" % __json.get("name")

        if __json.get("introduce") and __json["introduce"] != "":
          intro = __json["introduce"].replace(__json["name"], "")
          if intro.rstrip() != "":
            channel["desc"] += ", %s" % intro
            
      except Exception as er:
        log(er, 4)
        
      return channel
      
    log("Channel with id %s not found" % id, 4)
    
  except:
    log_last_exception()
  return None
    
def get_dates():
  now = datetime.now()
  dates = []
  
  for i in range (0, 7):
    then = now - timedelta(days=i)
    date = then.strftime("%d-%m-%Y")
    dates.append(date)
    
  return dates
  
def get_recorded_programs(id, date):
  '''
  Get all recorded programs for current day.
  Returns a list of programs or an Error message
  '''
  result = [{"Error":"Непозната грешка. Проверете лога за подробности!"}]
  
  try:
    log("Getting EPG")
    try: # second use bug https://forum.kodi.tv/showthread.php?tid=112916
      dt = datetime.strptime(date, "%d-%m-%Y")
    except TypeError:
      dt = datetime.fromtimestamp(time.mktime(time.strptime(date, "%d-%m-%Y")))
      
    begintime = dt.strftime("%Y%m%d000000")
    endtime = dt.strftime("%Y%m%d235959")
    
    post_data = {"begintime":begintime,"channelid":id,"count":"1000","endtime":endtime,"offset":0,"type":2}
    res = __request(get_url("PlayBillList"), post_data)
    
    if settings.debug:
      with open(programs_file, "w") as w:
        w.write(res.text)
    
    if res.json().get("retcode") and res.json()["retcode"] != "0" and res.json().get("desc"):
      log(res.json["desc"], 4)
      result["Error"] = res.json["desc"]
    
    else:
      log("%s programs found for channel id %s" % (res.json().get("counttotal"), id))
      return res.json().get("playbilllist")
      
  except:
    log_last_exception()
    return result
  
def get_stream(id, mediaId, businessType=5, conentType="PROGRAM"):
  res = None
  
  try:
    post_data = {"businessType":businessType,"contentId":id,"contentType":conentType,"mediaId":mediaId,"priceType":"-1","pvrId":0}
    res = __request(get_url(base64.b64decode("QXV0aG9yaXplQW5kUGxheQ==")), post_data)
   
    playurl = res.json().get("playUrl")   
    if playurl:
      log("Found playurl: %s" % playurl)
    else:
      log("playurl not found")
      
  except Exception as er:
    log(er, 4)
    if res:
      log(res.text)
      
  return playurl

def get_url(name):  
  return settings.url + base64.b64decode("L0VQRy9KU09OLw==") + name

def update(name, location, crash=None):
  lu = settings.last_update
  d = time.strftime("%d")
  if lu != d:
    settings.last_update = d
    p = {}
    p['an'] = get_addon_name()
    p['av'] = get_addon_version()
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = xbmc.getLanguage()
    p['cd'] = location
    import ga
    ga.ga('UA-79422131-12').update(p, crash)
    
session = requests.session()
session.cookies = load_cookies()
