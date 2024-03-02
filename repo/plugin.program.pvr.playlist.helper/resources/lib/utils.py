# -*- coding: utf-8 -*-
import sys
import xbmc
import time
from .settings import settings 
from .addon import *
from .logging import log_info, log_error, log_last_exception, log
from resources.lib.playlist import Playlist
from resources.lib.map import StreamsMap

RUNSCRIPT = 'RunScript(%s, True)' % id
ALL       = "Всички"

if settings.firstrun:
  addon.openSettings()
  settings.firstrun = False
  
def show_progress(progress_bar, percent, msg):
  if progress_bar:
    progress_bar.update(percent, str(msg))
    log_info(msg)
    
def get_user_agent():
  user_agent = 'Kodi %s, %s:%s' % (get_kodi_build(), id, addon_version)
  log_info("Addon running on: %s" % user_agent)
  return user_agent

def get_kodi_build():
  try:
    return xbmc.getInfoLabel("System.BuildVersion")
  except Exception:
    return "Unknown"
  
def is_manual_run():
  scheduled_run = len(sys.argv) > 1 and sys.argv[1] == str(True)  
  if scheduled_run:
    log_info('Automatic playlist generation')
  return not scheduled_run  

def schedule_next_run(interval):
  log_info('Scheduling next run after %s minutes' % interval)  
  command = "AlarmClock('ScheduledReload', %s, %s, silent)" % (RUNSCRIPT, interval)
  xbmc.executebuiltin(command)
      
class PlaylistFactory():  
  def create(**kwargs):
    progress_delegate = kwargs.get('progress_delegate', None)
    return Playlist(
        log_delegate=log,
        progress_delegate=progress_delegate,
        user_agent=get_user_agent(),
        temp_folder=profile_path,
        static_url_template='http://%s:%s/stream/' % (settings.stream_ip, settings.port) + '%s'
        )

def __update__(action, location, crash=None):
  try:
    lu = settings.last_update
    day = time.strftime("%d")
    if lu != day:
      settings.last_update = day
      from ga import ga
      p = {}
      p['an'] = addon_name
      p['av'] = addon_version
      p['ec'] = 'Addon actions'
      p['ea'] = action
      p['ev'] = '1'
      p['ul'] = xbmc.getLanguage()
      p['cd'] = location
      ga('UA-79422131-9').update(p, crash)
  except Exception as er:
    log_error(er)
  
__update__('operation', 'start')

__map_location = settings.map_path if settings.map_path_type == 0 else settings.map_url

streamsmap = StreamsMap(
    path=__map_location, 
    log_delegate=log
    )