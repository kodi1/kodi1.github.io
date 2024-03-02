import os
import xbmcaddon
import xbmcvfs

id            = 'plugin.program.tvbgpvr.backend'
addon         = xbmcaddon.Addon()
addon_version = addon.getAddonInfo('version')
addon_name    = addon.getAddonInfo('name')
profile_path  = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
addon_path    = xbmcvfs.translatePath(addon.getAddonInfo('path'))
resource_path = xbmcvfs.translatePath(os.path.join(addon_path, 'resources'))