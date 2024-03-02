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

from urllib.parse import quote_plus, urlencode

import sys
import inputstreamhelper

import xbmc
import xbmcgui
import xbmcplugin

from . import api
from . import view

APP = "100005a"
BASE_API = "https://api.viki.io"

UA = "Mozilla/5.0 (Macintosh; MacOS X10_14_3; rv;93.0) Gecko/20100101 Firefox/93.0"  # За симулиране на заявка от  компютърен браузър


def search(args):
    """Search menu"""
    keyb = xbmc.Keyboard("", "Search in VIKI® Database")
    keyb.doModal()

    if keyb.isConfirmed() and len(keyb.getText()) > 0:
        search_text = quote_plus(keyb.getText())
        search_text = search_text.replace(" ", "+")
        searchurl = args.series_id + "?per_page=40&term=" + search_text
        index(args, searchurl)


def genre(args):
    """List all genre"""
    jsonrsp = api.request("videos/genres.json", None)
    for _, i in enumerate(jsonrsp):
        url = (
            args.series_id
            + ".json?sort=newest_video&per_page=40&genre="
            + i["id"]
        )
        # add to view
        view.add_item(
            args,
            {
                "title": i["name"]["en"],
                "mediatype": "addons",
                "mode": "index",
                "series_id": url,
            },
            isFolder=True,
        )

    view.endofdirectory(args)
    return True


def country(args):
    """List all country"""
    jsonrsp = api.request("videos/countries.json", None)
    for i, subdict in jsonrsp.items():
        url = (
            args.series_id
            + ".json?sort=newest_video&per_page=40&origin_country="
            + i
        )
        lang = subdict["name"].get(args.lang)
        if not lang:
            lang = subdict["name"]["en"]

        view.add_item(
            args,
            {"title": lang, "mediatype": "addons", "mode": "index", "series_id": url},
            isFolder=True,
        )

    view.endofdirectory(args)
    return True


def index(args, searchurl=""):
    """Display content"""
    if searchurl:
        args.series_id = searchurl

    if hasattr(args, "offset"):
        url = args.series_id + "&page=" + args.offset
    else:
        url = args.series_id + "&page=1"

    jsonrsp = api.request(url + "&per_page=40", None)

    # check for error
    if "response" not in jsonrsp:
        view.add_item(args, {"title": args.addon.getLocalizedString(30061)})
        view.endofdirectory(args)
        return False

    p_dialog = xbmcgui.DialogProgressBG()
    p_dialog.create("Viki", "Loading elements...")
    count = 0
    total = len(jsonrsp["response"])

    for _, movie in enumerate(jsonrsp["response"]):
        count += 1
        i_percent = int(float(count * 100) / total)
        p_dialog.update(i_percent, message="Loading elements...")

        try:
            titles = movie["titles"][args.lang]
        except KeyError:
            titles = movie["titles"]["en"]

        try:
            poster = str(movie["images"]["atv_cover"]["url"])
        except KeyError:
            poster = str(movie["images"]["poster"]["url"])

        try:
            mdes = movie["descriptions"][args.lang]
        except KeyError:
            try:
                mdes = movie["descriptions"]["en"]
            except KeyError:
                mdes = ""
        try:
            dur = str(movie["duration"])
        except KeyError:
            dur = ""
        try:
            rating = movie["rating"]
        except KeyError:
            rating = ""

        types = "tvshows" if movie["type"] == "series" else "movies"
        if types == "tvshows":
            url = f'{BASE_API}/v4/series/{movie["id"]}/episodes.json?per_page=40&app={APP}'
        else:
            try:
                url = str(movie["watch_now"]["id"])
            except KeyError:
                url = str(movie["id"])

        # add to view
        view.add_item(
            args,
            {
                "title": titles,
                "plot": mdes,
                "duration": dur,
                "rating": rating,
                "thumb": poster,
                "fanart": poster,
                "mediatype": types,
                "series_id": url if types == "tvshows" else url,
                "episode_id": url if types == "movies" else "",
                "mode": "listEpisode" if types == "tvshows" else "videoplay",
            },
            isFolder=True if types == "tvshows" else False,
        )

    if len(jsonrsp["response"]) == 40:
        view.add_item(
            args,
            {
                "title": args.addon.getLocalizedString(30055),
                "offset": int(getattr(args, "offset", 1)) + 1,
                "mode": args.mode,
                "mediatype": "tvshows",
                "series_id": args.series_id,
            },
            isFolder=True,
        )

    p_dialog.close()
    view.endofdirectory(args)
    return True


def episode(args):
    """Display episode"""
    if hasattr(args, "offset"):
        url = args.series_id + "&page=" + args.offset
    else:
        url = args.series_id + "&page=1"

    jsonrsp = api.request(url, None)

    # check for error
    if jsonrsp.get("error"):
        view.add_item(args, {"title": args.addon.getLocalizedString(30061)})
        view.endofdirectory(args)
        return False

    p_dialog = xbmcgui.DialogProgressBG()
    p_dialog.create("Viki", "Loading elements...")
    count = 0
    total = len(jsonrsp["response"])

    for i in range(0, len(jsonrsp["response"])):
        count += 1
        i_percent = int(float(count * 100) / total)
        p_dialog.update(i_percent, message="Loading elements...")

        try:
            titles = str(jsonrsp["response"][i]["titles"][args.lang])
        except KeyError:
            try:
                titles = str(jsonrsp["response"][i]["titles"]["en"])
            except KeyError:
                titles = jsonrsp["response"][i]["container"]["titles"]["en"]

        ep_num = str(jsonrsp["response"][i]["number"])
        url = str(jsonrsp["response"][i]["id"])
        poster = str(jsonrsp["response"][i]["images"]["poster"]["url"])
        dur = str(jsonrsp["response"][i]["duration"])
        rating = str(jsonrsp["response"][i]["rating"])

        # add to view
        view.add_item(
            args,
            {
                "title": titles,
                "episode": ep_num,
                "duration": dur,
                "rating": rating,
                "thumb": poster,
                "fanart": poster,
                "mediatype": "episodes",
                "series_id": args.series_id,
                "episode_id": url,
                "mode": "videoplay",
            },
            isFolder=False,
        )

    if len(jsonrsp["response"]) == 40:
        view.add_item(
            args,
            {
                "title": args.addon.getLocalizedString(30055),
                "offset": int(getattr(args, "offset", 1)) + 1,
                "mode": args.mode,
                "mediatype": "addons",
                "series_id": args.series_id,
            },
            isFolder=True,
        )

    p_dialog.close()
    view.endofdirectory(args)
    return True


def startplayback(args):
    """Parse MPD and start playback"""
    jsonrsp = api.request(
        f"playback_streams/{args.episode_id}.json?token={args.auth_token}&drms=dt3",
        None,
        version=5,
    )

    if jsonrsp.get("error"):
        # Refresh token
        if jsonrsp.get("error") == "invalid token":
            args.addon.setSetting("auth_token", "")
            jsonrsp = api.request(
                f"playback_streams/{args.episode_id}.json?token={args.auth_token}&drms=dt3",
                None,
                version=5,
            )
        elif jsonrsp.get("error") == "Unauthorized request":
            xbmcgui.Dialog().ok(
                "Viki",
                args.addon.getLocalizedString(30306),
            )
            return
        else:
            xbmcgui.Dialog().ok(
                "Viki",
                jsonrsp.get("details"),
            )
            return


    base64elem = api.request(
        f"videos/{args.episode_id}/drms.json?offline=false&stream_ids={jsonrsp['main'][0]['properties']['track']['stream_id']}&dt=dt3&token={args.auth_token}",
        None,
        version=5,
    )
    manifest_url = base64elem["dt3"]

    headers = {
        "User-Agent": UA,
        "Referer": "https://www.viki.com/",
        "Origin": "https://www.viki.com",
    }

    is_helper = inputstreamhelper.Helper("mpd", drm="com.widevine.alpha")
    if is_helper.check_inputstream():
        if jsonrsp:
            li = xbmcgui.ListItem(
                path="http://127.0.0.1:4920/url=" + jsonrsp["main"][0]["url"]
            )
            li.setMimeType("application/xml+dash")
            li.setContentLookup(False)

            li.setProperty("inputstream", "inputstream.adaptive")
            li.setProperty("inputstream.adaptive.manifest_type", "mpd")
            li.setProperty("inputstream.adaptive.license_type", "com.widevine.alpha")
            li.setProperty(
                "inputstream.adaptive.license_key",
                manifest_url + "|%s&Content-Type=|R{SSM}|" % urlencode(headers),
            )
            li.setProperty(
                "inputstream.adaptive.stream_headers",
                "User-Agent="
                + quote_plus(UA)
                + "&Origin=https://www.viki.com&Referer=https://www.viki.com",
            )
        else:
            xbmc.executebuiltin(
                f"Notification(VIKI®,  API does not return a result,  {4000},  OverlayLocked.png)"
            )

    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=li)
