# -*- coding: utf-8 -*-
import sys
from  xbmcplugin import setContent, endOfDirectory
from resources.lib.helper import *
from kodibgcommon.utils import get_params

params = get_params()
action = params.get("action")
id = params.get("id")

if action == None: 
  show_categories()
elif action == 'show_channels':
  show_channels(id)
elif action == 'show_streams':
  show_streams(id)
elif action == 'update_tvdb':
  update_tvdb()
else:
  play_channel(id)

setContent(int(sys.argv[1]), 'movies')
endOfDirectory(int(sys.argv[1]))
