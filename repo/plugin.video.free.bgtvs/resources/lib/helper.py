import os
import sys
import time
import xbmc
import sqlite3
import xbmcgui
import xbmcplugin
from .assets import DbAsset
from .playlist import *
from kodibgcommon.settings import settings
from kodibgcommon.utils import get_profile_dir, get_resources_dir, make_url, get_addon_name, get_addon_version
from kodibgcommon.logging import log_info, log_error, log
from kodibgcommon.notifications import notify_error, notify_success
       
#append_pydev_remote_debugger
if False:
    sys.path.append(os.environ["PYSRC"])
    sys.stdout = open(os.path.join(os.environ['TEMP'], 'stdout.txt'), 'w')
    sys.stderr = open(os.path.join(os.environ['TEMP'], 'stderr.txt'), 'w')
    import pydevd
    pydevd.settrace('127.0.0.1', stdoutToServer=False, stderrToServer=False)
#end_append_pydev_remote_debugger	

if settings.use_local_db and settings.db_file_path != '' and os.path.isfile(settings.db_file_path):
  db_file_path = settings.db_file_path
else:
  db_file_path = os.path.join( get_profile_dir(), 'tvs.sqlite3' )

def show_categories():
  update('browse', 'Categories')
  if not settings.use_local_db:
    asset = DbAsset(
      url=settings.url_to_db,
      log_delegate=log,
      file_path=db_file_path
    )
    if asset.is_expired():
      asset.update()
  log_info("Loading data from DB file: %s" % db_file_path)
  try:
    conn = sqlite3.connect(db_file_path)
    cursor = conn.execute('''SELECT * FROM freetvandradio_category''')
    li = xbmcgui.ListItem('Всички')
    url = make_url({"id": 0, "action": "show_channels"})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)
    for row in cursor:
      li = xbmcgui.ListItem(row[1])
      url = make_url({"id": row[0], "action": "show_channels"})
      xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, True)   
  except Exception as er:
    log_error(er)
    notify_error(er)
    
  if not settings.use_local_db:
    li = xbmcgui.ListItem('******** Обнови базата данни ********')
    url = make_url({"action": "update_tvdb"})
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li)    
  xbmcplugin.endOfDirectory(int(sys.argv[1]))

def show_channels(id):
  channels = get_channels(id)
  for c in channels:
    if not c.enabled and not settings.show_only_enabled:
      c.name = '[COLOR brown]%s[/COLOR]' % c.name
    li = xbmcgui.ListItem(c.name)
    li.setInfo( type = "Video", infoLabels = { "Title" : c.name } )
    li.setProperty("IsPlayable", str(False))
    url_items = {"id": c.id, "action": "show_streams"}
    url = make_url(url_items)  
    xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, li, False) 

def get_channels(category_id):
  '''
  '''
  channels = []
  log_info("Getting channel for category id: %s" % category_id)
  
  conn = sqlite3.connect(db_file_path)
  query = '''SELECT channel_id FROM freetvandradio_channel_category AS cc '''   
  # if we are showing all channels, that is category_id is 0 and show radios is disabled
  if int(category_id) > 0:
    query += "WHERE cc.category_id = %s;" % category_id
  
  conn.row_factory = lambda cursor, row: row[0]
  c = conn.cursor()
  ids = c.execute(query).fetchall()
  ids = ','.join(str(id) for id in ids)

  query_get_only_enabled = '''AND ch.enabled = 1''' if settings.show_only_enabled else ''
  query = '''SELECT ch.id, ch.name, ch.logo, ch.ordering, ch.enabled FROM freetvandradio_channel AS ch WHERE ch.id IN (%s) %s GROUP BY ch.id ORDER BY ch.ordering''' % (ids, query_get_only_enabled)
  conn.row_factory = lambda cursor, row: Channel(row)
  c = conn.cursor()
  channels = c.execute(query).fetchall()
  log_error("Extracted %s channels" % len(channels))
  return channels

def show_streams(channel_id):
  streams = get_streams(channel_id)
  select = 0
  if len(streams) > 1:
    dialog = xbmcgui.Dialog()
    select = dialog.select('Изберете стрийм', [s.comment for s in streams])
    if select == -1: 
      return False
  url = streams[select].url
  log_info('resolved url: %s' % url)
  item = xbmcgui.ListItem(path=url)
  item.setInfo( type = "Video", infoLabels = { "Title" : ''} )
  item.setProperty("IsPlayable", str(True))
  xbmcplugin.setResolvedUrl(int(sys.argv[1]), succeeded=True, listitem=item)
  
def get_streams(channel_id):
  '''
  '''
  streams = []
  conn = sqlite3.connect(db_file_path)
  query =  "SELECT s.id, s.channel_id, s.stream_url, s.page_url, s.player_url, s.enabled, s.comment, u.string AS user_agent, s.regex, s.stream_referer "
  query += "FROM freetvandradio_stream AS s "
  query += "JOIN freetvandradio_user_agent as u ON s.user_agent_id==u.id "
  query += "WHERE channel_id=%s" % channel_id
  if settings.show_only_enabled:
    query += " AND s.enabled=1"
  conn.row_factory = lambda cursor, row: Stream(row)
  c = conn.cursor()
  streams = c.execute(query).fetchall()
  return streams  

def play_channel(channel_id, stream_index = 0):
  try:
    urls = get_streams(id)
    s = urls[stream_index]
    li = xbmcgui.ListItem(s.name, iconImage=s.logo, thumbnailImage=s.logo, path=s.stream_url)
    li.setInfo( type = "Video", infoLabels = { "Title" : s.name } )
    li.setProperty("IsPlayable", 'True')
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
  except Exception as er:
    log_error(er)
    notify_error(er)
      
def update(name, location, crash=None):
  lu = settings.last_update
  day = time.strftime("%d")
  if lu == "" or lu != day:
    from ga import ga
    settings.last_update = day
    p = {}
    p['an'] = get_addon_name()
    p['av'] = get_addon_version()
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = xbmc.getLanguage()
    p['cd'] = location
    ga('UA-79422131-7').update(p, crash)

def update_tvdb():
  progress_bar = xbmcgui.DialogProgressBG()
  progress_bar.create(heading="Downloading db file...")
  msg = "Базата данни НЕ бе обновена!"
  try:
    log_info('Force-updating tvdb')
    asset = DbAsset(
      log_delegate=log,
      url=settings.url_to_db,
      file_path=db_file_path)
    progress_bar.update(1, "Downloading database...")
    res = asset.update()
    if res:
      msg = "Базата данни бе обновена успешно!"
    if settings.use_local_db:
      msg += " Използвате локална база данни!"
  except Exception as ex:
    log_error(ex)
    notify_error(ex, True)
  notify_success(msg)
  
  if progress_bar:
    progress_bar.close()
