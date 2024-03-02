# -*- coding: utf-8 -*-
#
#     Copyright (C) 2018 zinobg@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import urllib
from os import path, remove
from re import search, IGNORECASE
from xbmcvfs import translatePath
from xbmcgui import Dialog, NOTIFICATION_ERROR
from http.cookiejar import LWPCookieJar
# from xbmc import log

# setting up cookie jar
cj = LWPCookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)


# login to page
def doLogin(username, password, login_url, cookie_file):
    logged_in_string1 = 'logout'
    cookie_dir = path.join(translatePath('special://temp'))
    cookiepath = path.join(cookie_dir, cookie_file)
    # delete any old version of the cookie file
    try:
        remove(cookiepath)
    except:
        pass
    if username and password:
        payload = {'user': username, 'pass': password, 'remember': 'on'}
        data = urllib.parse.urlencode(payload)
        binary_data = data.encode('utf-8')
        req = urllib.request.Request(login_url, binary_data)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0')
        response = opener.open(req)
        source_login = response.read().decode('utf-8')
        response.close()
        if search(logged_in_string1, source_login, IGNORECASE):
            cj.save(cookiepath)
            return cookiepath
        else:
            Dialog().notification('[ Login ERROR ]', 'Login FAILED!', NOTIFICATION_ERROR, 10000, sound=True)
            raise SystemExit


# open an url using a cookie
def openUrl(url, cookiepath):
    try:
        cj.load(cookiepath, False, False)
    except:
        pass
    req = urllib.request.Request(url)
    response = opener.open(req)
    source = response.read().decode('utf-8')
    response.close()
    try:
        cj.save(cookiepath)
    except:
        pass
    return source
