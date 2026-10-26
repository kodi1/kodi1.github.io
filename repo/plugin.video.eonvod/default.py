import sys

import xbmcaddon
import xbmcvfs

sys.path.insert(0, xbmcvfs.translatePath(
    xbmcaddon.Addon().getAddonInfo("path") + "/resources/lib"))

import eonvod

eonvod.main()
