# -*- coding: utf8 -*-
import os
import re
import sys
import json
import urllib
#import cPickle
import requests
import logging 
from .stream import *
from .utils import *

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

class Playlist:
  streams = []
  channels = {}
  disabled_groups = []
  size = 0
  cache_file = ".cache"
  streams_file = ".streams"
  __map = {}

  def __init__(self, **kwargs):
    try:
      ## keyword arguments
      self.location = kwargs.get('location')
      self.progress_callback = kwargs.get('progress')
      self.name = kwargs.get('name', 'playlist.m3u')
      self.include_radios = kwargs.get('include_radios', False)
      self.template_file = kwargs.get('template_file', 'order.txt')
      self.user_agent = kwargs.get('user_agent')
      self.groups_from_progider = kwargs.get('groups_from_progider', False)
      self.type = kwargs.get('type', PlaylistType.KODIPVR)
      self.temp_folder = kwargs.get('temp_folder')
      if self.temp_folder:
        self.cache_file = os.path.join(self.temp_folder, self.cache_file)
        self.streams_file = os.path.join(self.temp_folder, self.streams_file)

      self.disabled_groups = kwargs.get('disabled_groups')
      log("Disabled groups: %s" % ",".join(self.disabled_groups))

      self.mapping_file = kwargs.get('mapping_file')
      self.__load_map()

      if self.location:
        self.__load()

      self.__serialize()

      log("Playlist initialized with %s channels" % self.count())
    except Exception as e:
      log("__init__() " + str(e), 4)
      raise

  def __progress(self, percent, msg):

    if self.progress_callback:
      self.progress_callback.update(percent, str(msg))

  def __load(self):
    '''
    Loads m3u from given location - local storage or online resource
    '''
    ret = True
    log("__load() started")
    self.__progress(5, "Loading playlist from: %s" % self.location)

    if self.location.startswith("http") or self.location.startswith("ftp"):
      ret = self.__download()

    if ret:
      self.__parse()

    log("__load() ended")

  def __download(self):
    try:
      headers = {}
      if self.user_agent:
        headers = {"User-agent": self.user_agent}

      log("Downloading resource from: %s " % self.location)
      response = requests.get(self.location, headers=headers)
      log("Server status_code: %s " % response.status_code)

      if response.status_code >= 200 and response.status_code < 400:
        chunk_size = self.__get_chunk_size__(response)
        self.__cache(self.__iter_lines__(response, chunk_size)) #using response.text.splitlines() is way too slow on singleboard devices!!!

      else:
        log("Unsupported status code received from server: %s" % response.status_code)
        return False

      return True

    except Exception as er:
      log(er, 4)
      return False

  def __get_chunk_size__(self, response):
    try:

      size = int(response.headers['Content-length'])
      if size > 0:
        return size/100

    except: pass

    return 2048

  def __iter_lines__(self, response, chunk_size, delimiter=None):
    '''
      Implementation of iter_lines to include a progress bar
    '''
    pending = None

    for chunk in response.iter_content(chunk_size=chunk_size, decode_unicode=True):

      if pending is not None:
        chunk = pending + chunk

      if delimiter:
        lines = chunk.split(delimiter)
      else:
        lines = chunk.splitlines()

      if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
        pending = lines.pop()
      else:
        pending = None

      for line in lines:
        yield line

    if pending is not None:
        yield pending

  def __cache(self, content):
    '''
    Saves the m3u locally and counts the lines
    Needed for the progress bar
    '''
    log("cache() started!")
    self.location = self.cache_file

    with open(self.location, "w") as file:
      for line in content:
        self.size += 1
        file.write("%s\n" % line.rstrip().encode("utf-8"))

    log("cache() ended!")

  def __parse(self):
    '''
      Parse m3u file line by line
    '''
    log("parse() started!")
    stream = None
    percent = 10
    max = 80
    step = round(self.size/max) if self.size > 0 else 16

    with open(self.location, "r") as file_content:
      for i, line in enumerate(file_content):
        if self.size > 0: # if true, we have counted the lines
          if i % step == 0:
            percent += 1
          self.__progress(percent, "Parsing playlist")

        if not line.startswith(START_MARKER):
          line = line.rstrip()

          if line and line.startswith(INFO_MARKER):
            stream = Stream(line, self.__map)

            ## create channels with various streams so that later we can extract streams with preffered quality
            if stream.id not in self.channels.iterkeys():
              log("Creating channel '%s', adding %s stream '%s'" % (stream.id, stream.quality, stream.name))
              channel = Channel()
              channel.name = stream.id.decode("utf-8")
              channel.streams[stream.quality] = stream
              self.channels[channel.name.decode("utf-8")] = channel

            else:
              log("Appending stream '%s' to channel '%s'" % (stream.name, stream.id))
              channel = self.channels[stream.id.decode("utf-8")]
              channel.streams[stream.quality] = stream
              log("Channel '%s' has %s streams" % (stream.id, len(self.channels[stream.id.decode("utf-8")].streams)))

          else:
            if not stream:
              continue

            stream.url = line
            stream.order = stream.get_order()
            self.streams.append(stream)

            stream = None #reset

    log("parse() ended")


  def __serialize(self):
    '''
    Serializes streams dict into a file so it can be used later
    '''
    log("__serialize() started")
    self.__progress(10, "Serializing streams")
    _streams = {}

    for stream in self.streams:
      _streams[stream.name] = stream.url

    log("serializing %s streams in %s" % (len(_streams), self.streams_file))
    #cPickle.dump(_streams, open(self.streams_file, "wb"))

    with open(self.streams_file, "w") as w:
      w.write(json.dumps(_streams, ensure_ascii=False))

    log("__serialize() ended")


  def reorder(self, **kwargs):
    '''
      Reorders channels in the playlist
      Keyword Args:
        template_file: a template txt file with channel names. Single name on each a row
    '''
    log("reorder() started")
    self.template_file = kwargs.get('template_file', self.template_file)
    template_order = self.__load_order_template()
    percent = 95
    max = 3
    step = round(len(self.streams)/max)
    log("Reordering streams")

    for i, stream in enumerate(self.streams):
      if i % step == 0:
        percent += 1
      self.__progress(percent, "Reordering playlist")

      try:
        stream.order = template_order[stream.name]
        log ("'%s'=%s - order found in order.txt file" % (stream.name, stream.order))
        # Streams in template should always be added to the playlist
        # So enable stream is_favored property
        stream.is_favored = True

      except:
        log("'%s'=%s - ordered by original stream id" % (stream.name, stream.order))
        pass

    self.streams = sorted(self.streams, key=lambda stream:stream.order)
    log("reorder() ended")


  def __load_order_template(self):

    template_order = {}

    try:
      with open(self.template_file) as file_content:
        log("Reading template file %s " % self.template_file)

        for i, line in enumerate(file_content):
          template_order[line.rstrip()] = i
          log("%s=%s" % (line.rstrip(), i))

    except Exception as er:
      log(er, 4)

    return template_order

  def add(self, new_m3u_location):
    '''
    Adds channels from new playlist to current one
    '''
    self.load(new_m3u_location)

  def count(self, count_disabled_channels=True):

    if count_disabled_channels:
      return len(self.streams)

    else:
      i = 0

      for stream in self.streams:
        if stream.group not in self.disabled_groups:
          i += 1

      return i

  def __to_string(self, type):
    '''
      Outputs the current streams into different formats
    '''
    log("__to_string() started!")
    self.__progress(98, "Saving playlist. Type: %s" % type)
    if not type:
      type = self.type

    buffer = ""
    percent = 0
    n = len(self.streams)
    # step = round(n/100)
    enabled_streams = 0

    for i in range(0, n):
      # if i % step == 0:
        # percent += 1
      # self.__progress(percent, "1. Saving playlist. Type: %s" % type)
      # Disable streams from disabled groups or streams with offset (only when hide_timeshifted is enabled)
      if self.streams[i].group in self.disabled_groups or (self.streams[i].offset and settings.hide_timeshifted):
        self.streams[i].disabled = True

      if self.streams[i].is_favored or not self.streams[i].disabled or type == PlaylistType.NAMES or type == PlaylistType.JSON:
        stream_string = self.streams[i].to_string(type)
        enabled_streams += 1
        if type == PlaylistType.JSON: #append comma
          if i < (n-1): stream_string += ","
        buffer += stream_string

    if type == PlaylistType.KODIPVR or type == PlaylistType.PLAIN:
      buffer = "%s\n%s" % (START_MARKER, buffer)

    if type == PlaylistType.JSON:
      buffer = "[%s]" % buffer

    log("__to_string() returned %s streams" % enabled_streams)
    return buffer.encode("utf-8", "replace")


  def __load_map(self):
    '''
    Downloads mapping file. If downloads fails loads the local file.
    '''

    self.__progress(2, "Downloading map file")

    try:
      #if os.environ.get('TVBGPVRDEBUG'):
      #  raise Exception('Debug mode enabled. Fail the download and force local playlist.')

      url = "https://raw.githubusercontent.com/harrygg/EPG/master/maps/channels-tvbg.json"
      headers = {"Accept-Encoding": "gzip, deflate"}
      log("Downloading streams map from: %s " % url)
      response = requests.get(url, headers=headers)
      log("Map server status code: %s " % response.status_code)
      log("Map size: %s " % response.headers["Content-Length"])

      if response.status_code < 200 and response.status_code >= 400:
        raise Exception("Unsupported status code!")

      self.__map = response.json()

    except Exception as ex:
      log("Downloading map failed!", 4)
      log(ex, 4)
      self.__map = {"date": "0", "revision": "0", "streams": {}, "groups": {}}

    log("Loaded map. Date %s, Rev. %s, Channels %s, Groups %s" % (self.__map["date"], self.__map["revision"], len(self.__map["streams"]), len(self.__map["groups"])))


  def save(self, **kwargs):
    '''
    Saves current playlist into a file
    Kwargs:
      path - path to the file where the playlist will be saved.
        If no path is given and the playlist is loaded from file
        it will be overwritten. If no path is given and the
        playlist is loaded from url, it will be saved in the current folder
      type - the type of playlist
    '''

    # If no path is provided overwite current file
    file_path = kwargs.get('path', self.cache_file)
    type = kwargs.get('type', self.type)

    try:

      with open(file_path, 'w') as file:
        log("Saving playlist type %s in %s " % (str(type), file_path))
        file.write(self.__to_string(type))
      return True

    except Exception as er:

      log(er, 4)
      return False

  def set_static_stream_urls(self, url):
    '''
    Replaces all stream urls with static ones
    That point to our proxy server
    '''
    for stream in self.streams:
      name = urllib.quote(stream.name.encode("utf-8"))
      stream.url = url % (name)


  def set_preferred_quality(self, preferred_quality, forced_disable=False):
    '''
    Disables streams that are not of preferred quality, enable all others
    Args:
      preferred_quality: The preffered quality of the channel - UHD, HD, SD or LQ
      forced_disable: Should a channel be disabled if it has no alternative qualities. Defaults to False
        Example:
        If a channel has only one stream and forced_disable is False, the stream will be enabled
        regardless of its quality. If a channel has more than one streams but none of them matches
        the preferred_quality, the logic will select the highest available quality.
    '''
    _streams = []

    try:
      log("set_preferred_quality() started")
      i = 0
      percent = 90
      max = 5
      step = round(len(self.channels) / max)

      for channel_name, channel in self.channels.iteritems():
        if i % step == 0:
          percent += 1
        self.__progress(percent, "Selecting %s streams for channel %s" % (preferred_quality, channel_name))
        i += 1
        __preferred_quality = preferred_quality
        log("Searching for '%s' stream from channel '%s'" % (__preferred_quality, channel_name))

        ### change quality if there is no stream with the preferred_quality
        if not channel.streams.get(__preferred_quality):
          __preferred_quality = HD if __preferred_quality == SD else SD
          log("No %s stream for channel '%s'. Changing quality to %s" % (preferred_quality, channel_name, __preferred_quality))

        # disable streams with unpreferred quality
        for quality,stream in channel.streams.iteritems():

          if quality == __preferred_quality:
            stream.disabled = False
            log("Preferred %s stream found. Adding '%s'" % (stream.quality, stream.name))
          else:
            ## if it's a channel with a single stream, add it.
            if len(channel.streams) == 1 and not forced_disable:
              stream.disabled = False
              log("Adding '%s' stream '%s' (single stream, quality setting is ignored)" % (stream.quality, stream.name))
            else:
              log("Disabling unpreferred '%s' stream %s" % (stream.quality, stream.name))
              stream.disabled = True
          _streams.append(stream)

      self.streams = _streams

    except Exception as er:
      log(er)

    log("Filtered %s channels with preferred quality"% len(self.streams) )
    log("set_preferred_quality() ended!")
