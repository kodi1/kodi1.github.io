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

import inputstreamhelper
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

from . import api
from . import view
from . import model
from . import controller
from .util import convert_lang


def main(argv):
    """Main function for the addon"""
    args = model.parse(argv)

    # inputstream adaptive settings
    if hasattr(args, "mode") and args.mode == "hls":
        is_helper = inputstreamhelper.Helper("hls")
        if is_helper.check_inputstream():
            xbmcaddon.Addon(id="inputstream.adaptive").openSettings()
        return True

    args.auth_token = args.addon.getSetting("auth_token")
    args.user_id = args.addon.getSetting("user_id")

    # get subtitle language
    args.lang = convert_lang(args.addon.getSetting("lang"))

    # login
    if api.start(args):
        # list menue
        xbmcplugin.setContent(int(args.argv[1]), "addons")
        check_mode(args)
        api.close(args)
    else:
        # login failed
        xbmc.log(f"[PLUGIN] {args.addonname}: Login failed", xbmc.LOGERROR)
        view.add_item(args, {"title": args.addon.getLocalizedString(30061)})
        view.endofdirectory(args)
        xbmcgui.Dialog().ok(args.addonname, args.addon.getLocalizedString(30061))
        return False


def check_mode(args):
    """Run mode-specific functions"""
    if hasattr(args, "mode"):
        mode = args.mode
    else:
        mode = None

    if not mode:
        show_main_menue(args)
    elif mode == "search":
        controller.search(args)
    elif mode == "index":
        controller.index(args)
    elif mode == "listEpisode":
        controller.episode(args)
    elif mode == "genre":
        controller.genre(args)
    elif mode == "contry":
        controller.country(args)
    elif mode == "videoplay":
        controller.startplayback(args)
    elif mode in ("series", "film"):
        show_categories_menue(args, mode)
    else:
        # unkown mode
        xbmc.log(
            f"[PLUGIN] {args.addonname}: Failed in check_mode '{mode}'",
            xbmc.LOGERROR,
        )
        xbmcgui.Dialog().notification(
            args.addonname,
            args.addon.getLocalizedString(30061),
            xbmcgui.NOTIFICATION_ERROR,
        )
        show_main_menue(args)


def show_main_menue(args):
    """Show main menu"""
    # Search
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30040),
            "mode": "search",
            "series_id": "search.json",
        },
    )
    view.add_item(
        args, 
        {
            "title": args.addon.getLocalizedString(30038), 
            "mode": "film",
        },
    )
    view.add_item(
        args, 
        {
            "title": args.addon.getLocalizedString(30039), 
            "mode": "series",
        },
    )
    # Latest clip
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30054),
            "mode": "index",
            "series_id": "clips.json?sort=newest_video",
        },
    )
    view.endofdirectory(args)


def show_categories_menue(args, genre):
    """Show categories menue"""
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30042),
            "mode": "genre",
            "series_id": "movies" if genre == "film" else genre,
        },
    )
    # By Country
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30043),
            "mode": "contry",
            "series_id": "movies" if genre == "film" else genre,
        },
    )

    # Latest
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30044),
            "mode": "index",
            "series_id": "containers.json?sort=release_date&type=" + genre,
        },
    )
    # Recent popular
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30045),
            "mode": "index",
            "series_id": "containers.json?sort=views_recent&type=" + genre,
        },
    )
    # Trending
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30046),
            "mode": "index",
            "series_id": "containers.json?sort=views&type=" + genre,
        },
    )
    # Best
    view.add_item(
        args,
        {
            "title": args.addon.getLocalizedString(30047),
            "mode": "index",
            "series_id": "containers.json?sort=average_rating&type=" + genre,
        },
    )
    view.endofdirectory(args)
