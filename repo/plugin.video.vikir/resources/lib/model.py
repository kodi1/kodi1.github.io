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
try:
    from urlparse import parse_qs
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import parse_qs, unquote_plus

import xbmcaddon


def parse(argv):
    """Decode arguments"""
    if argv[2]:
        return Args(argv, parse_qs(argv[2][1:]))
    else:
        return Args(argv, {})


class Args(object):
    """Arguments class
    Hold all arguments passed to the script and also persistent user data and
    reference to the addon. It is intended to hold all data necessary for the
    script.
    """

    def __init__(self, argv, kwargs):
        """Initialize arguments object
        Hold also references to the addon which can't be kept at module level.
        """
        self.argv = argv
        self.addonid = self.argv[0][9:-1]
        self.addon = xbmcaddon.Addon(id=self.addonid)
        self.addonname = self.addon.getAddonInfo("name")

        for key, value in kwargs.items():
            if value:
                setattr(self, key, unquote_plus(value[0]))
