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

from urllib.parse import quote_plus

import xbmcvfs
import xbmcgui
import xbmcplugin
import xbmc


# keys allowed in setInfo
types = [
    "count",
    "size",
    "date",
    "genre",
    "country",
    "year",
    "episode",
    "season",
    "sortepisode",
    "top250",
    "setid",
    "tracknumber",
    "rating",
    "userrating",
    "watched",
    "playcount",
    "overlay",
    "cast",
    "castandrole",
    "director",
    "mpaa",
    "plot",
    "plotoutline",
    "title",
    "originaltitle",
    "sorttitle",
    "duration",
    "studio",
    "tagline",
    "writer",
    "tvshowtitle",
    "premiered",
    "status",
    "set",
    "setoverview",
    "tag",
    "imdbnumber",
    "code",
    "aired",
    "credits",
    "lastplayed",
    "album",
    "artist",
    "votes",
    "path",
    "trailer",
    "dateadded",
    "mediatype",
    "dbid",
]


def endofdirectory(args):
    # let xbmc know the script is done adding items to the list
    xbmcplugin.endOfDirectory(handle=int(args.argv[1]))


def add_item(args, info, isFolder=True):
    """Add item to directory listing."""
    # create list item
    li = xbmcgui.ListItem(label=info["title"])

    # get infoLabels
    infoLabels = make_infolabel(args, info)

    # get url
    u = build_url(args, info)
    mediatype = infoLabels.get("mediatype", "addons")

    if not isFolder:
        li.setProperty("IsPlayable", "true")

    # set media image
    li.setArt(
        {
            "thumb": info.get("thumb", "DefaultFolder.png"),
            "poster": info.get("thumb", "DefaultFolder.png"),
            "banner": info.get("thumb", "DefaultFolder.png"),
            "fanart": info.get(
                "fanart", xbmcvfs.translatePath(args.addon.getAddonInfo("fanart"))
            ),
            "icon": info.get("thumb", "DefaultFolder.png"),
        }
    )

    # Nexus compatibility.
    if not xbmc.getInfoLabel("system.buildversion")[0:2] >= "20":
        li.setInfo("video", infoLabels)
    else:
        videoInfoTag = li.getVideoInfoTag()
        videoInfoTag.setMediaType("episode" if mediatype == "episodes" else mediatype)
        videoInfoTag.setTitle(infoLabels.get("title", ""))
        videoInfoTag.setTvShowTitle(infoLabels.get("title", ""))
        videoInfoTag.setPlot(infoLabels.get("plot", ""))
        try:
            videoInfoTag.setRating(float(infoLabels.get("rating", 0.0)))
        except ValueError:
            # Movie return classification.
            videoInfoTag.setMpaa(infoLabels.get("rating"))
        videoInfoTag.setDuration(int(infoLabels.get("duration", 0)))
        videoInfoTag.setSeason(int(infoLabels.get("season", 1)))
        videoInfoTag.setEpisode(int(infoLabels.get("episode", 0)))

    xbmcplugin.setContent(
        int(args.argv[1]), "videos" if mediatype == "addons" else mediatype
    )

    if mediatype == "episodes":
        xbmcplugin.addSortMethod(
            int(args.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED, labelMask="%H. %T"
        )

    # add item to list
    xbmcplugin.addDirectoryItem(
        handle=int(args.argv[1]), url=u, listitem=li, isFolder=isFolder
    )


def quote_value(value):
    """Quote value depending on python"""
    if not isinstance(value, str):
        value = str(value)
    return quote_plus(value.encode("utf-8") if isinstance(value, str) else value)


def build_url(args, info):
    """Create url"""
    s = ""
    # step 1 copy new information from info
    for key, value in list(info.items()):
        if value:
            s = s + "&" + key + "=" + quote_value(value)

    # step 2 copy old information from args, but don't append twice
    for key, value in list(args.__dict__.items()):
        if value and key in types and not "&" + str(key) + "=" in s:
            s = s + "&" + key + "=" + quote_value(value)
    return args.argv[0] + "?" + s[1:]


def make_infolabel(args, info):
    """Generate infoLabels from existing dict"""
    infoLabels = {}
    # step 1 copy new information from info
    for key, value in list(info.items()):
        if value and key in types:
            infoLabels[key] = value

    # step 2 copy old information from args, but don't overwrite
    for key, value in list(args.__dict__.items()):
        if value and key in types and key not in infoLabels:
            infoLabels[key] = value

    return infoLabels
