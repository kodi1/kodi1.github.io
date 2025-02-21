# -*- coding: utf-8 -*-
import os
import io
import sys
import json
import time
import xbmc
import xbmcaddon
import xbmcvfs  # Use xbmcvfs for file operations

class Settings():

  def __getattr__(self, name):
    temp = this.getSetting(name)
    if (name != "debug"):
      log ("getting setting %s=%s" % (name, temp))
    if temp.lower() == 'true':
      return True
    elif temp.lower() == 'false':
      return False
    elif temp.isdigit():
      return int(temp)
    else:
      return temp

  def __setattr__(self, name, value):
    this.setSetting(name, str(value))

def log(msg, level=xbmc.LOGDEBUG):
  try:
    if settings.debug and level == xbmc.LOGDEBUG:
      level = xbmc.LOGINFO
    xbmc.log('%s | %s' % (id, str(msg)), level)
  except Exception as e:
    try:
      xbmc.log('%s | Logging failure: %s' % (id, e), level)
    except:
      pass

def show_progress(progress_bar, percent, msg):
  if progress_bar:
    progress_bar.update(percent, str(msg))
    log(msg)

def notify(msg):
  log("notify() %s" % msg)
  command = "Notification(%s,%s,%s)" % (translate(32003), msg, 5000)
  xbmc.executebuiltin(command)

def notify_error(msg):
  log("notify_error() %s" % msg)
  command = "Notification(%s,%s,%s)" % (translate(32005), msg, 5000)
  xbmc.executebuiltin(command)

def __update__(action, location, crash=None):
  try:
    lu = settings.last_update
    day = time.strftime("%d")
    if lu != day:
      settings.last_update = day
      from ga import ga
      p = {}
      p['an'] = this.getAddonInfo('name')
      p['av'] = this.getAddonInfo('version')
      p['ec'] = 'Addon actions'
      p['ea'] = action
      p['ev'] = '1'
      p['ul'] = xbmc.getLanguage()
      p['cd'] = location
      ga('UA-79422131-10').update(p, crash)
  except Exception as er:
    log(er)

def get_template_file():
    template_file = settings.template_file
    if not xbmcvfs.exists(template_file):  # Replaced xbmc with xbmcvfs
        cwd = xbmcvfs.translatePath(this.getAddonInfo('path'))  # Corrected for Kodi 21
        template_file = xbmcvfs.translatePath(cwd + '/resources/order.txt')  # Ensured proper path handling
    return template_file

def get_disabled_groups():
  disabled_groups = []
  if settings.hide_children:
    disabled_groups.append('Детски')
  if settings.hide_docs:
    disabled_groups.append('Документални')
  if settings.hide_french:
    disabled_groups.append('Френски')
  if settings.hide_english:
    disabled_groups.append('Английски')
  if settings.hide_german:
    disabled_groups.append('Немски')
  if settings.hide_holland:
    disabled_groups.append('Холандски')
  if settings.hide_italian:
    disabled_groups.append('Италиански')
  if settings.hide_movies:
    disabled_groups.append('Филми')
  if settings.hide_music:
    disabled_groups.append('Музикални')
  if settings.hide_news:
    disabled_groups.append('Новини')
  if settings.hide_russian:
    disabled_groups.append('Руски')
  if settings.hide_serbian:
    disabled_groups.append('Сръбски')
  if settings.hide_theme:
    disabled_groups.append('Тематични')
  if settings.hide_turkish:
    disabled_groups.append('Турски')
  if settings.hide_xxx:
    disabled_groups.append('Възрастни')
  if settings.hide_sports:
    disabled_groups.append('Спортни')
  if settings.hide_bulgarian:
    disabled_groups.append('Български')
  if settings.hide_asia:
    disabled_groups.append('Азиатски')
  if settings.hide_greek:
    disabled_groups.append('Гръцки')
  if settings.hide_roman:
    disabled_groups.append('Румънски')
  if settings.hide_others:
    disabled_groups.append('Други')
  if settings.hide_information_pr:
    disabled_groups.append('information')
  if settings.hide_movies_pr:
    disabled_groups.append('cinema')
  if settings.hide_news_pr:
    disabled_groups.append('news')
  if settings.hide_docs_pr:
    disabled_groups.append('documentary')
  if settings.hide_sports_pr:
    disabled_groups.append('sports')
  if settings.hide_entertainments_pr:
    disabled_groups.append('entertainments')
  if settings.hide_russian_pr:
    disabled_groups.append('Russian')
  if settings.hide_music_pr:
    disabled_groups.append('music')
  if settings.hide_children_pr:
    disabled_groups.append('children\'s')
  if settings.hide_xxx_pr:
    disabled_groups.append('for adults')
  if settings.hide_free_pr:
    disabled_groups.append('free web tv')
  if settings.hide_culture_pr:
    disabled_groups.append('culture')
  if settings.hide_greek_pr:
    disabled_groups.append('greek')
  if settings.hide_roman_pr:
    disabled_groups.append('romanian')

  return disabled_groups

def get_location():
  location = settings.url + settings.mac
  if os.environ.get('TVBGPVRDEBUG'):
    location = os.environ['TVBGPVRDEBUG']
  return location

def get_stream_url(name):
  """
  Reads stream list from cache and returns url of the selected stream name
  """
  try:
    # deserialize streams
    # streams = cPickle.load(open(pl_streams))
    streams = json.load(io.open(pl_streams, encoding='utf-8'))
    log("Deserialized %s streams from file %s" % (len(streams), pl_streams))
    return streams.get(name)
  except Exception as er:
    log(er)
    return None

## Initialize the addon
id            = 'plugin.program.tvbgpvr.backend'
this          = xbmcaddon.Addon()
translate     = this.getLocalizedString
settings      = Settings()
pl_name       = 'playlist.m3u'
profile_dir   = xbmcvfs.translatePath(this.getAddonInfo('profile'))  # Replaced xbmc with xbmcvfs
pl_path       = xbmcvfs.translatePath(profile_dir + '/playlist.m3u')
pl_cache      = xbmcvfs.translatePath(profile_dir + '/.cache')
pl_streams    = xbmcvfs.translatePath(profile_dir + '/.streams')
__version__   = xbmc.getInfoLabel('System.BuildVersion')
VERSION       = int(__version__[0:2])
user_agent    = 'Kodi %s' % __version__
scheduled_run = len(sys.argv) > 1 and sys.argv[1] == str(True)
addon_dir     = this.getAddonInfo('path')
mapping_file  = xbmcvfs.translatePath(addon_dir + '/resources/mapping.json')
progress_bar  = None

### Literals
RUNSCRIPT     = 'RunScript(%s, True)' % id
GET           = 'GET'
HEAD          = 'HEAD'
NEWLINE       = '\n'
BIND_IP       = '0.0.0.0' if settings.bind_all else '127.0.0.1'
STREAM_URL    = 'http://' + settings.stream_ip + ':' + str(settings.port) + '/tvbgpvr.backend/stream/%s'
HD            = 'HD'
SD            = 'SD'
LQ            = 'LQ'
START_MARKER  = "#EXTM3U"
INFO_MARKER   = "#EXTINF"
ALL           = "Всички"

### Addon starts
if settings.firstrun:
  this.openSettings()
  settings.firstrun = False

__update__('operation', 'start')

class PlaylistType:
  KODIPVR = "KODIPVR"
  PLAIN   = "PLAIN"
  NAMES   = "NAMES"
  JSON    = "JSON"
