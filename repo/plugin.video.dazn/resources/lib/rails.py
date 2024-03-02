# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class Rails:


    def __init__(self, plugin, i):
        self.item = {}
        self.plugin = plugin
        self.item['mode'] = 'rail'
        self.item['title'] = i.get('Title')
        self.item['id'] = i.get('Id')
        self.item['plot'] = None
        if i.get('Params', ''):
            self.item['params'] = i['Params']
