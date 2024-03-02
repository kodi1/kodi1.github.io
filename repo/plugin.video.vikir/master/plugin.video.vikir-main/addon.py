# -*- coding: utf-8 -*-
"""# Viki
# Base structure by 2018 MrKrabat
# Adapted for Viki by Arias800
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>."""
import sys
import xbmc
import xbmcaddon


# plugin constants
addon = xbmcaddon.Addon(id=sys.argv[0][9:-1])
_PLUGIN = addon.getAddonInfo("name")
_VERSION = addon.getAddonInfo("version")

xbmc.log(f"[PLUGIN] {_PLUGIN}: version {_VERSION} initialized")

if __name__ == "__main__":
    from resources.lib import viki

    # start addon
    viki.main(sys.argv)
