# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode


class Context:


    def __init__(self, plugin):
        self.cm = []
        self.plugin = plugin


    def epg_date(self):
        d = {
            'mode': 'epg',
            'id': 'date'
        }
        self.cm.append((self.plugin.get_string(30230), 'ActivateWindow(Videos, {0})'.format(self.plugin.build_url(d))))
        return self.cm


    def live(self, item):
        d = {
            'mode': 'play_context_from_beginning',
            'title': py2_encode(item['title']),
            'id': item.get('id', ''),
            'params': item.get('params', ''),
            'verify_age': item.get('verify_age', False)
        }
        self.cm.append((self.plugin.get_string(12021), 'RunPlugin({0})'.format(self.plugin.build_url(d))))
        return self.cm


    def highlights(self, item, mode):
        d = {
            'mode': mode,
            'title': py2_encode(item['title']),
            'id': item.get('id', ''),
            'params': item.get('params', '')
        }
        self.cm.append((self.plugin.get_string(30231), 'Container.Update({0})'.format(self.plugin.build_url(d))))
        return self.cm


    def related(self, cm_items):
        for i in cm_items:
            type_ = self.plugin.get_resource('{0}{1}Title'.format(i['type'][0].lower(), i['type'][1:]), 'browseui_').get('text')
            if type_.endswith('Title'):
                type_ = i['type']
            d = {
                'mode': 'play_context',
                'title': py2_encode(i['title']),
                'id': i.get('id', ''),
                'params': i.get('params', '')
            }
            self.cm.append((type_, 'RunPlugin({0})'.format(self.plugin.build_url(d))))
        return self.cm


    def goto(self, item):
        if item.get('sport', None):
            i = item['sport']
            d = {
                'mode': 'rails',
                'title': py2_encode(i['Title']),
                'id': 'sport',
                'params': i['Id']
            }
            self.cm.append((self.plugin.get_string(30214), 'Container.Update({0})'.format(self.plugin.build_url(d))))

        if item.get('competition', None):
            i = item['competition']
            d = {
                'mode': 'rails',
                'title': py2_encode(i['Title']),
                'id': 'competition',
                'params': i['Id']
            }
            self.cm.append((self.plugin.get_string(30215), 'Container.Update({0})'.format(self.plugin.build_url(d))))

        return self.cm
