# -*- coding: utf-8 -*-
import uuid
import xbmcplugin
from resources.lib.actions import *

if settings.rebuild_user_data or not settings.guid:
  settings.username = ""
  settings.password = ""
  settings.rebuild_user_data = False
  settings.open()
  settings.guid = uuid.uuid4()

params  = get_params()
id      = params.get("id")
mediaId = params.get("mediaId")
name    = params.get("name")
date    = params.get("date")
action  = params.get("action")

if action == None:
  show_channels()
elif action == 'show_channel':
  show_channel(id)
elif action == 'show_days':
  show_days(id)
elif action == 'show_recordings':
  show_recordings(id, date)
elif action == 'show_recording':
  show_recording(id, mediaId, name)
elif action == 'show_settings':
  settings.open()

xbmcplugin.endOfDirectory(int(sys.argv[1]))