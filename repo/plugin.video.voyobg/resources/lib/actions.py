# -*- coding: utf-8 -*-
import base64
import requests
from urllib import quote_plus
from jsonrpc import *
from kodibgcommon.utils import *

def userLogin():
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  params = {"username":settings.username,"password":settings.password}
  batch.append( rpc.userLogin(params) )
  res = batch.execute()
  log(res)
  res = batch.get_result_by_id(id)
  if res and res.get("session") and res["session"] != "":
    settings.session = res["session"]
    return True
  return False

def deviceGet():
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  params = {"session":settings.session}
  batch.append( rpc.deviceGet(params) )
  res = batch.execute()
  log(res)
  res = batch.get_result_by_id(id)
  devices = {}
  if res.get("list") and len(res["list"]) > 0:
    devices["names"] = []
    devices["ids"] = []
    for dev in res["list"]:
      devices["names"].append(dev["dName"])
      devices["ids"].append(dev["deviceId"])
  return devices

def deviceIsRegistered():
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  params = {"session":settings.session,"device":settings.device_id}
  batch.append( rpc.deviceIsRegistered(params) )
  res = batch.execute()
  log(res)
  res = batch.get_result_by_id(id)
  if res.get("isRegistered"):
    return True
  return False

def deviceRegister():
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  dName = "Kodi_%s_%s" % (get_kodi_major_version(), get_platform())
  params = {"session":settings.session,"dCode":"ANDROID","dName":dName,"dHash":settings.device_id,"ext":{"os":"Android","version":"6.0","rooted":"false"}}
  batch.append( rpc.deviceRegister(params) )
  res = batch.execute()
  log(res)
  res = batch.get_result_by_id(id)
  if res.get("error"):
    return res.get("errorMsg")
  return False  

def deviceRemove(deviceId):
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  params = {"session":settings.session,"deviceId":deviceId}
  batch.append( rpc.deviceRemove(params) )
  res = batch.execute()
  log(res)
  res = batch.get_result_by_id(id)
  return res.get("removed")
  
def sectionProducts(sectionId, limit=21):
  id = 1
  batch = JsonBatch()
  rpc = JsonRpc(id)
  params = {"sectionId":sectionId,"chargingType":"SP","paging":{"offset":0,"count":limit},"imageSize":{"mainImage":"480x640"},"attr":["productId","title","mainImage","hasChildren","pcRating","distributions","video"]}
  
  batch.append(rpc.sectionProducts(params))
  res = batch.execute()
  log(res)
  res = batch.get_result_by_id(id)
  items = []
  if res.get("list") and res.get("count") and res["count"] > 0:
    log("%s items found" % res["count"])
    for l in res["list"]:
      item = {}
      try: item["title"] = l["title"].split("|")[1]
      except: item["title"] = l["title"]      
      try: item["mediaId"] = l["video"]["lv"][0]
      except: 
        try: item["mediaId"] = l["video"]["ln"][0]
        except: item["mediaId"] = None
      item["productId"] = l["productId"]
      item["logo"] = l.get("mainImage")
      item["distributionId"] = l.get("distributionId")
      items.append(item)
  return items

def encryptKey(hash, productId, mediaId):
  try:
    t = base64.b64decode('eyJtZWQiOiVzLCJsaWMiOiVzLCJwcm9kIjolcywiZGV2IjolcywiYWlkIjoiIn0=') % (mediaId, hash, productId, settings.device_id)
    log("raw: %s" % t)
    t = base64.b64encode(t)
    log("injected key: %s" % t)
    return quote_plus(t)
  except:
    log("Error creating key", 4)
    return ""

def getProductUrl(mediaId, productId):
  batch = JsonBatch()
  rpc = JsonRpc(1)
  params = {"productId":productId,"session":settings.session,"device":settings.device_id}
  batch.append( rpc.userAccess(params) )
  
  rpc = JsonRpc(2)
  params = {"mediaId":mediaId,"mediaFormat":["M3U8"],"deliveryProtocol":["hlslivetv"]}
  batch.append( rpc.media(params) )
  
  res = batch.execute()
  res = batch.get_result_by_id(1)
  log(res)
  item = {}
  if not res.get("isAllowed"):
    item["isAllowed"] = False
    try: item["errors"] = res.get("messages").itervalues().next()
    except: item["errors"] = "Product not allowed!"
    return item
  
  hash = res["hash"]
  res = batch.get_result_by_id(2)
  log(res)
  
  url = res["mediaLocations"][0]["url"]
  key = encryptKey(hash, productId, mediaId)
  item["url"] = "%s?%s" % (url, key)
  item["isAllowed"] = True
  log("item[\"isAllowed\"]: %s" % item["isAllowed"])
  log("item[\"url\"]: %s" % item["url"])
  return item
  
def update(name, location, crash=None):
  import time
  import ga
  lu = settings.last_update
  day = time.strftime("%d")
  if lu == "" or lu != day:
    settings.last_update = day
    p = {}
    p['an'] = get_addon_name()
    p['av'] = get_addon_version()
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = xbmc.getLanguage()
    p['cd'] = location
    ga.ga('UA-79422131-13').update(p, crash)  
