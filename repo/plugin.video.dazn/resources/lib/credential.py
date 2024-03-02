# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode
from base64 import b64encode, b64decode
from Cryptodome.Cipher import DES3
from Cryptodome.Util.Padding import pad, unpad
from time import sleep
from uuid import NAMESPACE_DNS, uuid5

import xbmc
import xbmcgui


class Credential(object):


    def __init__(self, plugin):
        self.plugin = plugin


    def encode(self, data):
        key_handle = DES3.new(self.uniq_id(), DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
        encrypted = key_handle.encrypt(pad(data.encode('utf-8'), DES3.block_size))
        return b64encode(encrypted)


    def decode(self, data):
        if data == '':
            return data

        key_handle = DES3.new(self.uniq_id(), DES3.MODE_CBC, iv=b'\0\0\0\0\0\0\0\0')
        decrypted = unpad(key_handle.decrypt(b64decode(data)), DES3.block_size)
        return decrypted.decode('utf-8')


    def uniq_id(self):
        id = self.plugin.uniq_id()
        if len(id) > 24:
            id = id[:24]
        elif len(id) < 24:
            id = '{0}{1}'.format(id, (24 - len(id)) * '=')

        return id.encode('utf-8')


    def has_credentials(self):
        email = self.plugin.get_setting('email')
        password = self.plugin.get_setting('password')
        return email != '' and password != ''


    def set_credentials(self, email, password):
        _mail = self.encode(email) if email != '' else email
        _password = self.encode(password) if password != '' else password
        self.plugin.set_setting('email', _mail)
        self.plugin.set_setting('password', _password)


    def get_credentials(self):
        if self.plugin.get_setting('save_login') == 'true' and self.has_credentials():
            return {
                'email': self.decode(self.plugin.get_setting('email')),
                'password': self.decode(self.plugin.get_setting('password'))
            }
        else:
            email = self.plugin.get_dialog().input(self.plugin.get_resource('signin_emaillabel').get('text'), type=xbmcgui.INPUT_ALPHANUM)
            if '@' in email:
                password = self.plugin.get_dialog().input(self.plugin.get_resource('signin_passwordlabel').get('text'), type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
                if len(password) > 4:
                    return {
                        'email': email,
                        'password': password
                    }
        return {}


    def clear_credentials(self):
        user, password = '', ''
        self.plugin.set_setting('email', user)
        self.plugin.set_setting('password', password)
