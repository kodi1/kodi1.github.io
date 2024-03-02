# -*- coding: utf8 -*-
import os
import re
import time
import requests
from kodibgcommon.settings import settings
from kodibgcommon.logging import log_info, log_debug, log_error

class Category:
	def __init__(self, id, title):
		self.id = id
		self.title = title
    
class Channel:

  def __init__(self, attr):
    '''
    '''
    self.id = attr[0]
    self.name = attr[1]
    self.logo = attr[2]
    self.ordering = attr[3]
    self.enabled = attr[4] == 1
    #self.is_radio = 
    
  def to_string(self):
    '''
    '''
    output = '#EXTINF:-1 radio="False" tvg-shift=0 group-title="%s" tvg-logo="%s" tvg-id="%s",%s\n' % (self.category, self.logo, self.epg_id, self.name)
    output += '%s\n' % self.playpath
    return output 
 
class Stream:
  '''
  '''
  def __init__(self, attr):
    '''
    '''
    self.id = attr[0] 
    log_info("stream id=%s" % attr[0])
    self.channel_id = attr[1]
    log_info("channel_id=%s" % attr[1])
    self.url = attr[2]
    log_info("url=%s" % attr[2])
    self.page_url = attr[3]
    self.player_url = attr[4]
    self.enabled = attr[5] == 1
    self.comment = attr[6]
    self.user_agent = False if attr[7] is None else attr[7]
    self.regex = False if attr[8] is None else attr[8]
    self.referer = False if attr[9] is None else attr[9]
    if self.url == None or self.url == "":
      log_info("Resolving playpath url from %s" % self.player_url)
      self.url = self.resolve()
    if self.url is not None and self.user_agent: 
      self.url += '|User-Agent=%s' % self.user_agent
    if self.url is not None and self.referer:
      self.url += '&Referer=%s' % self.referer
    log_info("Stream final playpath: %s" % self.url)
    
  def resolve(self):
    stream = None
    s = requests.session()
    headers = {'User-agent': self.user_agent, 'Referer':self.page_url}
    
    # If btv - custom dirty fix to force login
    # if self.channel_id == 2:
    #   body = { "username": settings.btv_username, "password": settings.btv_password }
    #   headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    #   r = s.post("https://btvplus.bg/lbin/social/login.php", headers=headers, data=body)
    #   log_info(r.text)
    #   if r.json()["resp"] != "success":
    #     log_error("Проблем при вписването в сайта btv.bg")
    #     return None

    self.player_url = self.player_url.replace("{timestamp}", str(time.time() * 100))
    log_info(self.player_url)
    r = s.get(self.player_url, headers=headers)
    # log_info("body before replacing escape backslashes: " + r.text)
    body = r.text.replace('\\/', '/').replace("\\\"", "\"")
    # log_info("body after replacing escape backslashes: " + body)

    regex = self.regex if self.regex else '(//.*?\.m3u.*?)[\s\'"]{1}'
    log_info("Regex used: %s" % regex)
    matches = re.compile(regex).findall(body)
    if len(matches) > 0:
      log_info('Found %s matches in %s' % (len(matches), self.player_url))
      if not matches[0].startswith('http'):
        if self.player_url.startswith("https"):
          stream = "https:" + matches[0]
        elif self.player_url.startswith("http"):
          stream = "http:" + matches[0]
      else:
        stream = matches[0]
        log_info('Extracted stream %s' % stream)
    else:
      log_error("No matches found for m3u extraction")
      log_debug("Response body: \n" + body)
      
    return stream
