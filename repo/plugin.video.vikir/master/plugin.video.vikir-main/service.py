# -*- coding: utf-8 -*-
"""# Copyright: (c) 2020, SylvainCecchetto, wwark
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)

# This file is part of Catch-up TV & More"""
import re
import sys
import requests
import xbmcaddon

try:  # Python 3
    from http.server import BaseHTTPRequestHandler
except ImportError:  # Python 2
    from BaseHTTPServer import BaseHTTPRequestHandler

try:  # Python 3
    from socketserver import TCPServer
except ImportError:  # Python 2
    from SocketServer import TCPServer

addon = xbmcaddon.Addon(id="plugin.video.vikir")

PY3 = sys.version_info >= (3, 0, 0)


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Simple server"""
    def do_GET(self):
        """Get function"""
        result = requests.get(url=self.path.split("url=")[-1], timeout=10).text
        new_mpd = re.search(r'thumbnail_tile".+?\s*<BaseURL>(.+?)<', result)
        if new_mpd:
            self.path = new_mpd.group((1))
            tempres = requests.get(url=self.path, timeout=10).text

            get_sub = re.search(
                r"thumbnail_tile.+?Representation>(.*)",
                result,
                re.MULTILINE | re.DOTALL,
            ).group((1))
            data = re.findall("<BaseURL>(.+?)<", tempres)
            for d in data:
                tempres = tempres.replace(
                    d,
                    "https://m-content-viki.s.llnwi.net/"
                    + self.path.split("/")[3]
                    + "/dash/"
                    + d,
                )
            tempres = tempres.rsplit("\n", 4)[0]
            result = tempres + get_sub

        self.send_response(200)
        self.end_headers()
        self.wfile.write(result.encode("utf-8"))


ADDRESS = "127.0.0.1"  # Localhost

PORT = 4920

server_inst = TCPServer((ADDRESS, PORT), SimpleHTTPRequestHandler)
# The follow line is only for test purpose, you have to implement a way to stop the http service!
server_inst.serve_forever()
