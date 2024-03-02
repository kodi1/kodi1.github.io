# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from urllib.parse import quote_plus
from .simple_requests.api import Request


class Playback:


    def __init__(self, plugin, data):
        self.plugin = plugin
        self.ManifestUrl = ''
        self.LaUrl = ''
        self.CdnToken = ''
        self.Cdns = []
        self.get_detail(data.get('PlaybackPrecision', {}), data.get('PlaybackDetails', []))


    def clean_name(self, cdns):
        return [cdn.replace('live', '').replace('vod', '') for cdn in cdns]


    def get_detail(self, precision, details):
        if precision.get('Cdns'):
            self.Cdns = self.clean_name(precision['Cdns'])
        if self.Cdns:
            cdn = self.plugin.get_cdn(self.Cdns)
            if cdn:
                self.parse_detail(details, cdn)
            else:
                for i in self.Cdns:
                    self.parse_detail(details, i)
                    if self.ManifestUrl:
                        break
        if not self.ManifestUrl:
            self.parse_detail(details)


    def parse_detail(self, details, cdn=''):
        for i in details:
            if cdn == self.clean_name([i['CdnName']])[0] or not cdn:
                url = '{}{}{}={}'.format(i['ManifestUrl'], '&' if i['ManifestUrl'].find('?') > -1 else '?', i['CdnToken']['Name'], quote_plus(i['CdnToken']['Value']))
                r = Request(self.plugin).head(url, headers={'user-agent': self.plugin.get_user_agent()})
                if r.status_code == 200 and self.plugin.get_dict_value(r.headers, 'content-type').startswith('application/dash+xml'):
                    self.ManifestUrl = url
                    self.LaUrl = i['LaUrl']
                    self.CdnToken = '{}={}'.format(i['CdnToken']['Name'], quote_plus(i['CdnToken']['Value']))
                    break
