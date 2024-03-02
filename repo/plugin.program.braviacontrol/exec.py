# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import re
import simplejson as json
import urllib.request, urllib.parse, urllib.error
from ga import ga
import requests

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__language__ = __addon__.getLocalizedString
__cwd__ = xbmcvfs.translatePath( __addon__.getAddonInfo('path') )
__profile__ = xbmcvfs.translatePath( __addon__.getAddonInfo('profile') )
__resource__ = xbmcvfs.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
__icon_msg__ = xbmcvfs.translatePath( os.path.join( __cwd__, 'resources', 'logo.png' ) )
__cmdf__ = xbmcvfs.translatePath( os.path.join( __profile__, 'dat' ) )

sys.path.insert(0, __resource__)

headers = {'Content-Type': 'text/xml; charset=UTF-8',
           'SOAPACTION': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"',
           }

def Notify (msg1, msg2):
  xbmc.executebuiltin(('Notification(%s,%s,%s,%s)' % (msg1, msg2, '5000', __icon_msg__)))

def update(name, dat, crash=None):
  payload = {}
  payload['an'] = __scriptname__
  payload['av'] = __version__
  payload['ec'] = name
  payload['ea'] = 'sony_ctrl'
  payload['ev'] = '1'
  payload['dl'] = urllib.parse.quote_plus(dat)
  ga().update(payload, crash)

if __addon__.getSetting('firstrun') == 'true':
  Notify('Settings', 'empty')
  __addon__.openSettings()
  __addon__.setSetting('firstrun', 'false')

if not __addon__.getSetting('host'):
  Notify('Host', 'empty')
if not __addon__.getSetting('pin'):
  Notify('PIN', 'empty')
if not __addon__.getSetting('mac'):
  Notify('MAC', 'empty')

headers['X-Auth-PSK'] = __addon__.getSetting('pin')

def wakeup():
  import struct, socket
  update('WOL', 'WOL')
  add_oct = __addon__.getSetting('mac').split(':')
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  # hwa = '\x00\x21\x6A\xC7\x1A\x42'
  hwa = struct.pack('BBBBBB', int(add_oct[0],16),
                      int(add_oct[1],16),
                      int(add_oct[2],16),
                      int(add_oct[3],16),
                      int(add_oct[4],16),
                      int(add_oct[5],16))
  s.sendto(b'\xff'*6 + hwa*16, (__addon__.getSetting('host'), 80))
  s.close()

def runsh():
  tmp = __addon__.getSetting('run')
  update('exec', tmp)
  if tmp:
    xbmc.executebuiltin('System.Exec(%s)' % (tmp))

def get_crls(ip):
  cmds = {}
  codes_cmd = '{"method":"getRemoteControllerInfo","params":[],"id":10,"version":"1.0"}'
  r = s.post('http://%s/sony/system' % ip, headers=headers, data=codes_cmd, timeout=2.0)
  for e in r.json()['result'][1]:
    cmds.update({e['name']: e['value']})
  return cmds

def set_ctrl(ip, code):
  cmd = "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"><IRCCCode>%s</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>" % code
  s.post('http://%s/sony/IRCC' % ip, headers=headers, data=cmd, timeout=2.0)

def dbg_msg(msg):
  if dbg:
    print('### %s: %s' % (__scriptid__, msg))

import traceback

s = requests.Session()
s.mount('http://', adapter = requests.adapters.HTTPAdapter(max_retries=20))

try:
  if len(sys.argv) == 2 and sys.argv[1] == "WOL":
    wakeup()
  elif len(sys.argv) == 2 and sys.argv[1] == "EXEC":
    runsh()
  else:
    if os.path.exists(__cmdf__):
      with open(__cmdf__, 'r') as f:
        c = json.load(f)
    else:
      c = get_crls(__addon__.getSetting('host'))
      with open(__cmdf__, 'wb+') as f:
        f.write(json.dumps(c, sort_keys = True, indent = 1))

    if len(sys.argv) == 1:
      ls = []
      for lst in list(c.keys()):
        ls.append(lst)
      dialog = xbmcgui.Dialog()
      n = dialog.select('Select command', ls)
      cmd = ls[n]
    else:
      cmd = sys.argv[1]

    if cmd in list(c.keys()):
      update(cmd, c[cmd])
      set_ctrl(__addon__.getSetting('host'), c[cmd])
    else:
      raise ValueError('%s Fail' % cmd)

except Exception as e:
  Notify('Error', 'Fail')
  traceback.print_exc()
  update('exception', str(e.args[0]), sys.exc_info())
  pass

s.close()

