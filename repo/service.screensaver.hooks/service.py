# -*- coding: utf-8 -*-
import os, sys
import re
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from ga import ga
import simplejson as json

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__language__ = __addon__.getLocalizedString
__cwd__ = xbmcvfs.translatePath( __addon__.getAddonInfo('path') )
__profile__ = xbmcvfs.translatePath( __addon__.getAddonInfo('profile') )

dbg = False
if 'true' == __addon__.getSetting('dbg'):
  dbg = True

silent = not dbg

if 'true' == __addon__.getSetting('if_active'):
  if_active = True
else:
  if_active = False

if 'true' == __addon__.getSetting('if_active_i'):
  if_active_i = True
else:
  if_active_i = False

def update(actoin):
  payload = {}
  payload['an'] = __scriptname__
  payload['av'] = __version__
  payload['ec'] = 'screesaver_hooks'
  payload['ea'] = str(actoin)
  payload['ev'] = '1'
  ga().update(payload, None)

def log(msg):
  if dbg == True:
    xbmc.log(("%s *** %s" % (__scriptid__, msg,)),level=xbmc.LOGNOTICE)

class MyMonitor(xbmc.Monitor):
  def __init__(self, *args, **kwargs):
    xbmc.Monitor.__init__(self)

    self.__idle_t = 'System.IdleTime(5)'
    self.__idle_json = {
                    "jsonrpc": "2.0",
                    "method": "XBMC.GetInfoBooleans",
                    "params": {
                                "booleans": [self.__idle_t,]
                              },
                    "id": 1}

  #def onSettingsChanged(self):
    #self.update_settings()

  def onScreensaverActivated(self):
    if xbmc.Player().isPlaying() and 'true' == __addon__.getSetting('if_play'):
      delay = int(__addon__.getSetting('play_delay'))
    else:
      delay = int(__addon__.getSetting('delay'))

    if xbmc.Player().isPlaying() and 'true' == __addon__.getSetting('if_play_i'):
      delay_i = int(__addon__.getSetting('play_delay_i'))
    else:
      delay_i = int(__addon__.getSetting('delay'))

    log('Start screensaver hook')

    start = __addon__.getSetting('svr_activate')
    if start != '':
      log ('Start Delay %d min Exec: %s' % (delay, start))
      update('%s delay %d min' % (start, delay))
      xbmc.executebuiltin('AlarmClock (%s_cmd, System.Exec(%s), %s, %s)' % (__scriptid__, start, delay, silent))
      self.__if_active_ts = time.time() + (delay * 60)

    start_i = __addon__.getSetting('svr_activate_i')
    if start_i != '':
      log ('Start Delay %d min Exec: %s' % (delay_i, start_i))
      update('%s delay %d min' % (start_i, delay_i))
      xbmc.executebuiltin('AlarmClock (%s_addon, RunScript(%s), %s, %s)' % (__scriptid__, start_i, delay_i, silent))
      self.__if_active_ts_i = time.time() + (delay_i * 60)

    start_ = __addon__.getSetting('svr_activate_instant')
    if start_ != '':
      log ('Start Exec: %s' % (start_,))
      update('%s instant' % (start_,))
      os.system('%s' % (start_,))
      #xbmc.executebuiltin('System.Exec(%s)' % start_)

  def onScreensaverDeactivated(self):
    log('Stop screensaver hook')

    stop_ = __addon__.getSetting('svr_deactivate_instant')
    if stop_ != '':
      log ('Start Exec: %s' % (stop_,))
      update('%s instant' % (stop_,))
      os.system('%s' % (stop_,))
      #xbmc.executebuiltin('System.Exec(%s)' % stop_)

    xbmc.sleep(1000)
    _data = json.loads(xbmc.executeJSONRPC(json.dumps(self.__idle_json)))
    log ('joson responce: %s' % (_data))
    if _data['result'][self.__idle_t]:
        log ('%s -> True' % (self.__idle_t))
        return

    xbmc.executebuiltin('CancelAlarm(%s_cmd, %s)' % (__scriptid__, silent))
    xbmc.executebuiltin('CancelAlarm(%s_addon, %s)' % (__scriptid__, silent))

    stop = __addon__.getSetting('svr_deactivate')
    if stop != '' and (False == if_active or time.time() > self.__if_active_ts):
      log ('Stop Exec: %s' % (stop,))
      update(stop)
      xbmc.executebuiltin('System.Exec(%s)' % (stop))
    else:
      log ('Not activated skip: %s' % (stop,))

      stop_i = __addon__.getSetting('svr_deactivate_i')
      if stop_i != '' and (False == if_active_i or time.time() > self.__if_active_ts_i):
        log ('Stop Exec: %s' % (stop_i,))
        xbmc.executebuiltin('RunScript(%s)' % (stop_i))
      else:
        log ('Not activated skip: %s' % (stop_i,))

if __name__ == '__main__':
  log('Monitor strt')
  update('Start')
  monitor = MyMonitor()
  while True:
    # Sleep/wait for abort for 3 seconds
    log ("Idle time: %d" % (xbmc.getGlobalIdleTime(),))
    if monitor.waitForAbort(3):
      # Abort was requested while waiting. We should exit
      break
  log('Exit')
  update('Stop')
  del monitor
