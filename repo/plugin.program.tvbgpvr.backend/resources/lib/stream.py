# -*- coding: utf8 -*-
import os
import logging
import re
import sys
import json
import string
from .utils import *

#importlib.reload(sys)
#sys.setdefaultencoding('utf8')  # This will still cause an error in Python 3

for filename in os.listdir(profile_dir):
  # Build the full file path
  file_path = os.path.join(profile_dir, filename)

  # Check if it's a file (not a directory)
  if os.path.isfile(file_path):
    try:
        # Open and read the file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Process the file content
            print(f"Content of {filename}:")
            print(content)  # You can replace this with your own processing logic
    except Exception as e:
        logging.error(f"Error reading {filename}: {e}")

class Stream:
  '''
    Class definition for m3u stream entries
  '''
  name      = None
  id        = None
  url       = None
  logo      = None
  group     = None
  shift     = None
  offset    = None
  is_radio  = False
  disabled  = False
  order     = 9999
  is_favored= False
  quality   = SD
  __props   = {}


  def __init__(self, line, map):

    self.line = line
    self.name = re.compile(',(?:\d+\.)*\s*(.*)').findall(self.line)[0]
    self.streams_map = map["streams"]
    self.groups_map = map["groups"]

    self.quality = self.__get_quality()
    self.id = self.name.replace(" %s" % self.quality, "").replace(str(self.quality), "").rstrip()

    log("Quality for stream '%s' set to %s" % (self.name, self.quality))
    # Get stream properties from the map of streams
    self.__get_stream_properties()

    # Overwrite stream name in case we have a new name.
    self.name = self.__props.get("n", self.name)
    # If no overwrite name is found remove any commas
    self.name = self.name.replace(",","")

    # Set ID
    try: self.id = self.__props["id"]
    except: pass
    log("Stream ID for channel '%s' set to '%s'" % (self.name, self.id))

    self.group = self.__get_group()
    self.logo = self.__get_logo()

    try:
      self.offset = re.compile('(\s\+\d+)').findall(self.name)[0]
      log("Channel '%s' is time shifted with %s" % (self.name, self.offset))
    except: pass

    try: self.shift = re.compile('shift[=\"\']+(.*?)["\'\s]+').findall(self.line)[0]
    except: pass


  def __get_stream_properties(self):
    try:
      self.__props = self.streams_map[self.name.decode("utf-8")]
      #log("Found map entry for channel %s" % self.name)
    except:
      if self.quality != SD:
        #log("Map entry for channel '%s' not found. Searching for '%s'" % (self.name, self.id))
        self.__props = self.streams_map.get(self.id.decode("utf-8"), {})
        #log("Found map entry for channel %s" % self.id)


  def __get_quality(self):
    if LQ in self.name:
      return LQ
    elif SD in self.name:
      return SD
    elif HD in self.name:
      return HD
    return SD


  def __get_group(self):
    group = None
    try:
      if settings.groups_from_progider:
        group = re.compile('group-title[="\']+(.*?)["\'\s]+').findall(self.line)[0]
      else:
        group_id = self.__props["g"]
        group = self.groups_map[group_id]
    except:
      ## Try go guess channel group from channel name
      lname = self.name.lower()
      if "spor" in lname:
        group = self.groups_map["st"]
      elif "movie" in lname or "film" in lname or "cinema" in lname:
        group = self.groups_map["mv"]
      elif "music" in lname:
        group = self.groups_map["mu"]
      elif "XX" in self.name:
        group = self.groups_map["xx"]
      elif "укр" in lname:
        group = self.groups_map["sr"]
      elif "pink" in lname:
        group = self.groups_map["sr"]
      elif "nl" in lname:
        group = self.groups_map["nl"]
      elif "RAI" in self.name:
        group = self.groups_map["it"]
      elif "TVR" in self.name or "RO" in self.name:
        group = self.groups_map["ro"]
      else:
        group = self.groups_map["ot"]

    log("Stream group set to '%s'" % group)
    return group


  def __get_logo(self):
    '''
    If no logo is in map, logo name is equal to the lowercase channel name removing any special chars
    and translating cyrilic to latin letters
    If logo is in map but without HTTP prefix, then that's the image name
    '''
    url = "https://raw.githubusercontent.com/harrygg/EPG/master/logos/%s.png"
    logo = None

    try:
      logo = self.__props["l"]
    except:
      name = re.sub(r'[\(\)&%/\!\:\.\s\'\*\,]*', '', self.name.decode("utf-8"))
      # replace delayed channel identificators i.e. +1 or +12
      name = re.sub(r'\+\d+', '', name)
      logo = name.replace(LQ, "").replace("+", "plus").replace("-", "minus").lower()
      try:
        # translate cyrilic chars to latin
        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                 u"abvgdeejziiklmnoprstufhzcssiyyeuaABVGDEEJZIIKLMNOPRSTUFHZCSS_Y_EUA")
        tr = dict( [ (ord(a), ord(b)) for (a, b) in zip(*symbols) ] )
        logo = logo.translate(tr)
      except:
        log("Translation of logo %s failed" % logo)

    if not logo.startswith("http"):
      logo = url % logo.lower()
    log("Logo for channel '%s' set to '%s'" % (self.name, logo))

    return logo

  def get_order(self):
    try:
      self.order = re.compile("stid=(\d+)").findall(self.url)[0]
    except:
      pass
    return self.order


  def to_string(self, type=PlaylistType.JSON):

    if type is PlaylistType.NAMES:
      return '%s\n' % self.name

    if type is PlaylistType.JSON:
      return '%s' % self.to_json()

    buffer = '%s:-1' % INFO_MARKER

    if type is not PlaylistType.PLAIN:
      if self.is_radio:
        buffer += ' radio="%s"' % self.is_radio
      if self.shift:
        buffer += ' tvg-shift="%s"' % self.shift
      if self.group:
        buffer += ' group-title="%s"' % self.group
      if self.logo:
        buffer += ' tvg-logo="%s"' % self.logo
      if self.id:
        buffer += ' tvg-id="%s"' % self.id

    buffer += ',%s\n' % self.name
    buffer += '%s\n' % self.url

    return buffer


  def to_json(self):
    '''
      Outputs the stream object into a JSON formatted string
    '''
    #return json.dumps({"name": self.name, "id": self.id, "url": self.url, "logo": self.logo, "group": self.group, "is_radio": self.is_radio, "shift": self.shift, "order": self.order, "quality": self.quality}, ensure_ascii=False).encode('utf8')
    return json.dumps({"name": self.name, "id": self.id}, ensure_ascii=False).encode('utf8')


class Channel:
  def __init__(self, name = None):
    self.streams = {} #dict with stream quality as a key
    self.name = name
