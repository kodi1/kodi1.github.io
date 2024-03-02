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
import time
import hashlib
import hmac
import json
import requests


class API:
    """Class handle every api call"""
    DEVICE_ID = "86085977d"
    APP = "100005a"
    APP_VERSION = "6.11.3"
    API_URL_TEMPLATE = "https://api.viki.io%s"
    APP_SECRET = (
        "d96704b180208dbb2efa30fe44c48bd8690441af9f567ba8fd710a72badc85198f7472"
    )
    session = None


def _api_query(path, version=4, **kwargs):
    path += "?" if "?" not in path else "&"
    query = f"/v{version}/{path}app={API.APP}"
    if "playback_streams/" in path or "drms.json" in path:
        query += "&device_id" + API.DEVICE_ID
    return query + "".join(f"&{name}={val}" for name, val in kwargs.items())


def _sign_query(path, version=4):
    timestamp = int(time.time())
    query = _api_query(path, version)
    sig = hmac.new(
        API.APP_SECRET.encode("ascii"),
        f"{query}&t={timestamp}".encode("ascii"),
        hashlib.sha1,
    ).hexdigest()
    return timestamp, sig, API.API_URL_TEMPLATE % query


def start(args):
    """Login and session handler"""

    # lets urllib handle cookies
    API.session = requests.Session()
    API.session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
        "x-viki-app-ver": API.APP_VERSION,
        "x-client-user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
        "Content-Type": "application/json; charset=utf-8",
        "X-Viki-manufacturer": "vivo",
        "X-Viki-device-model": "vivo 1606",
        "X-Viki-device-os-ver": "6.0.1",
        "X-Viki-connection-type": "WIFI",
        "X-Viki-carrier": "",
        "X-Viki-as-id": "100005a-1625321982-3932",
        "origin": "https://www.viki.com",
    }

    # get login informations
    username = args.addon.getSetting("viki_username")
    password = args.addon.getSetting("viki_password")

    # session management
    if not (args.user_id and args.auth_token):
        # create new session
        payload = {
            "password": password,
            "source": {
                "device": "vivo 1606",
                "method": "standard",
                "partner": "viki",
                "platform": "android",
            },
            "user": {
                "registration_method": "standard",
                "source_device": "vivo 1606",
                "source_partner": "viki",
                "source_platform": "android",
            },
            "username": username,
        }

        _, _, url = _sign_query("sessions.json", version=5)

        resp = API.session.post(url, json=payload).json()

        # check for error
        if resp.get("error"):
            return False
        args.auth_token = resp["token"]
        args.user_id = resp["user"]["id"]
    return True


def close(args):
    """Saves cookies and session"""
    args.addon.setSetting("user_id", args.user_id)
    args.addon.setSetting("auth_token", args.auth_token)


def destroy(args):
    """Destroys session"""
    args.addon.setSetting("user_id", "")
    args.addon.setSetting("auth_token", "")
    args.auth_token = ""


def request(method, options, query=None, version=4):
    """Viki API Call"""
    # required in every request
    payload = {}

    if "http" not in method:
        if query is None:
            timestamp, sig, url = _sign_query(method, version)
            API.session.headers.update(
                {"timestamp": str(timestamp), "signature": str(sig)}
            )
        else:
            url = API.API_URL_TEMPLATE % _api_query(method, version)
    else:
        url = method

    if options:
        # merge payload with parameters
        payload.update(options)
        response = API.session.get(url, data=json.dumps(payload))
    else:
        response = API.session.get(url)

    # parse response
    return response.json()
