# -*- coding: utf-8 -*-

from xbmcplugin import setContent, endOfDirectory
from resources.lib.dataprovider import try_db_update, show_categories, show_channels, show_streams, play_channel, update_db
from kodibgcommon.utils import get_params, get_addon_handle

params = get_params()
action = params.get("action")
itemid = params.get("id")

if action is None:
    try_db_update()
    show_categories()
elif action == 'show_channels':
    show_channels(itemid)
elif action == 'show_streams':
    show_streams(itemid)
elif action == 'update_tvdb':
    update_db()
else:
    play_channel(itemid)

setContent(get_addon_handle(), 'movies')
endOfDirectory(get_addon_handle())
