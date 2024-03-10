from xbmcplugin import endOfDirectory, setContent
from kodibgcommon.utils import get_params, get_addon_handle
from resources.lib import dataprovider
from xbmc import executebuiltin

params = get_params()
action_name = params.get("action", "show_categories")
view_mode = 500

action_delegate = getattr(dataprovider, action_name)
action_delegate(params)

endOfDirectory(get_addon_handle())
setContent(get_addon_handle(), 'movies')
executebuiltin("Container.SetViewMode(%s)" % view_mode)