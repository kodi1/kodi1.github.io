# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from six.moves.urllib.parse import parse_qs

import sys

import xbmcaddon

from resources.lib.client import Client
from resources.lib.common import Common
from resources.lib.credential import Credential
from resources.lib.parser import Parser

handle_ = int(sys.argv[1])
url_ = sys.argv[0]

plugin = Common(
    addon=xbmcaddon.Addon(),
    addon_handle=handle_,
    addon_url=url_
)
credential = Credential(plugin)
client = Client(plugin, credential)
parser = Parser(plugin)


def router(args):
    mode = args.get('mode', ['rails'])[0]
    title = args.get('title', [''])[0]
    id_ = args.get('id', ['home'])[0]
    params = args.get('params', [''])[0]
    verify_age = True if args.get('verify_age', [''])[0] == 'True' else False
    plugin.log("params = {0}".format(params))
    if mode == 'rails':
        parser.rails_items(client.rails(id_, params), id_)
    elif 'rail' in mode:
        parser.rail_items(client.rail(id_, params), mode)
    elif 'epg' in mode:
        date = params
        if id_ == 'date':
            date = plugin.get_date()
        parser.epg_items(client.epg(date), date, mode)
    elif mode == 'play':
        parser.playback(client.playback(id_, plugin.youth_protection_pin(verify_age)))
    elif 'play_context' in mode:
        parser.playback(client.playback(id_, plugin.youth_protection_pin(verify_age)), title, mode)
    elif mode == 'logout':
        if plugin.logout():
            credential.clear_credentials()
            client.signOut()
            sys.exit(0)
    elif mode == 'is_settings':
        plugin.open_is_settings()
    else:
        sys.exit(0)


if __name__ == '__main__':
    if plugin.get_setting('save_login') == 'false' and credential.has_credentials():
        credential.clear_credentials()

    paramstring = sys.argv[2][1:]
    args = dict(parse_qs(paramstring))

    if args.get('mode', ['rails'])[0] != 'logout' and (plugin.startup or not client.TOKEN):
        startup_data = client.initStartupData()
        endpoint_dict = plugin.init_api_endpoints(startup_data.get('ServiceDictionary'))
        client.initApiEndpoints(endpoint_dict)
        region = client.initRegion(startup_data)
        playable = plugin.start_is_helper()
        client.DEVICE_ID = plugin.uniq_id()
        if client.DEVICE_ID and playable:
            client.startUp(region)
            if client.TOKEN:
                plugin.set_setting('startup', 'false')
                client.userProfile()
        else:
            client.TOKEN = ''

    if client.TOKEN and client.DEVICE_ID:
        router(args)
    else:
        sys.exit(0)
