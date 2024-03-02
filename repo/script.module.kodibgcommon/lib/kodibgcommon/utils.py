# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import urllib.request, urllib.parse, urllib.error
import xbmcgui
import xbmcvfs
import xbmcaddon
import xbmcplugin

__addon__   = xbmcaddon.Addon()

def get_addon():
  return __addon__
  
def get_addon_id():
  return __addon__.getAddonInfo('id')
    
def get_addon_name():
  return __addon__.getAddonInfo('name')
    
def get_addon_version():
  return __addon__.getAddonInfo('version')

def translate(msg_id):
  return __addon__.getLocalizedString(msg_id)
  
def get_profile_dir():
  return xbmcvfs.translatePath( __addon__.getAddonInfo('profile'))

def get_addon_dir():
  return xbmcvfs.translatePath( __addon__.getAddonInfo('path'))
  
def get_resources_dir():
  return xbmcvfs.translatePath(os.path.join(get_addon_dir(), 'resources'))

def get_addon_icon():
  return xbmcvfs.translatePath( __addon__.getAddonInfo('icon'))
  
def get_platform():
  """Get platform
  Work through a list of possible platform types and return the first
  match. Ordering of items is important as some match more than one type.
  E.g. Android will match both Android and Linux
  """
  platforms = [
    "Android",
    "Linux.RaspberryPi",
    "Linux",
    "XBOX",
    "Windows",
    "ATV2",
    "IOS",
    "OSX",
    "Darwin",
  ]

  for platform in platforms:
    if xbmc.getCondVisibility('System.Platform.%s' % platform):
      return platform
  return "Unknown"

def get_kodi_build():
  try:
    return xbmc.getInfoLabel("System.BuildVersion")
  except Exception:
    return "Unknown"

def get_kodi_version():
  try:
    build = get_kodi_build()
    version = build.split(' ')[0]
    return version
  except:
    return "Unknown"

def get_kodi_major_version():
  version = get_kodi_version().split('.')[0]
  return int(version)

    
def get_kodi_language(): 
  xbmc.getLanguage()
  
def get_unique_device_id():
  import uuid
  return "KODI_%s_%s_%s" % (get_kodi_build(), get_platform(), uuid.uuid4())
  
def get_last_exception():
  import traceback
  traceback.format_exc(sys.exc_info())

###
### Navigation functions
###
def get_params(url=None):
  """
  Parses addon URL and returns a dict
  """
  dict = {}
  if not url:
    url = sys.argv[2]
  pairs = url.lstrip("?").split("&")
  for pair in pairs:
    if len(pair) < 3:
      continue
    kv = pair.split("=", 1)
    k = kv[0]
    v = urllib.parse.unquote_plus(kv[1])
    dict[k] = v
  return dict

def make_url(params, add_plugin_path=True):
  """
  Build a URL suitable for a Kodi add-on from a dict
  Prepends plugin path
  """
  pairs = []
  for k, v in params.items():
    k = urllib.parse.quote_plus(str(k))
    v = urllib.parse.quote_plus(str(v))
    pairs.append("%s=%s" % (k, v))
  params_str = "&".join(pairs)
  if add_plugin_path:
    return "%s?%s" % (sys.argv[0], params_str)
  return params_str

def get_addon_handle():
  """
  """
  try: 
    return int(sys.argv[1])
  except: 
    return -1  
  
def add_listitem_folder(title, url, **kwargs):
  """
  Add a directory list item
  """
  add_listitem(title, url, True, **kwargs)

                              
def add_listitem(title, url, isFolder=False, **kwargs):
  """
  Short syntax for adding a list item
  """
  li = xbmcgui.ListItem(title)
  xbmcplugin.addDirectoryItem(get_addon_handle(), url, li, isFolder)
                              

def add_listitem_unresolved(title, url, **kwargs):
  """
  """
  li = xbmcgui.ListItem(title)
  li.setInfo (type = "Video", infoLabels = { "Title" : ''} )
  li.setProperty("IsPlayable", 'True')  
  
  xbmcplugin.addDirectoryItem(get_addon_handle(), url, li, False)


def add_listitem_resolved_url(title, stream):
  """
  """
  li = xbmcgui.ListItem(title, path=stream)
  li.setInfo (type = "Video", infoLabels = { "Title" : ''} )
  li.setProperty("IsPlayable", 'True')  
  
  xbmcplugin.setResolvedUrl(get_addon_handle(), True, li)