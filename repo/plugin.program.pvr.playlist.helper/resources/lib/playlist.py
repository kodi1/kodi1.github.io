# -*- coding: utf8 -*-
import os
import sys
import requests
from .m3u_parser import PlaylistParser
from .enums import PlaylistType
from .map import StreamsMap
from .playlist_serializer import PlaylistSerializer
  
class Playlist:
  
  def __init__(self, **kwargs):
    
    self._log_delegate = kwargs.get('log_delegate', None)
    self.__log('Initializing playlist')
    self.name = kwargs.get('name', 'playlist.m3u')
    self.streams = []
    self.size = 0
    self._cache_file = kwargs.get('cache_file', '.cache')
    self._streams_file = ".streams"
    self.__streams_info_map = kwargs.get('map', StreamsMap())
    self._progress_delegate = kwargs.get('progress_delegate')
    self._progress_start_value = kwargs.get('progress_start', 20)
    self._progress_end_value = kwargs.get('progress_end', 80)
    self._user_agent = kwargs.get('user_agent')
    self._type = kwargs.get('type', PlaylistType.KODIPVR)
    self._temp_folder = kwargs.get('temp_folder')
    self._static_url_template = kwargs.get('static_url_template', None)
    if self._temp_folder:
      self._cache_file = os.path.join(self._temp_folder, self._cache_file)
      self._streams_file = os.path.join(self._temp_folder, self._streams_file)
      

  def load(self, resource_path):
    '''
      Loads a given resource. Automatically choses to load from file or from local path
    '''
    if resource_path.startswith('http') or resource_path.startswith('ftp'):
      return self.load_from_url(resource_path)
    return self.load_from_file(resource_path)


  def load_from_file(self, file_path):
    ''' 
    Loads m3u from local storage
    '''
    self.__log("load_from_file() started")
    self.__progress(5, "Loading playlist from: %s" % file_path)
    self.__parse_file(file_path)
    self.__log("load_from_file() ended")


  def load_from_url(self, url):
    '''
      Downloads the playlist from HTTP or FTP server
      Caches it on disk 
    '''
    result = True
    self.__log("load_from_url() started")
    self.__progress(5, "Loading playlist from: %s" % url)
    
    try:
      headers = {}
      if self._user_agent:
        headers = {"User-agent": self._user_agent}
        
      self.__log("Downloading resource from: %s " % url)
      response = requests.get(url, headers=headers)
      self.__log("Server status_code: %s " % response.status_code)
      
      if response.status_code >= 200 and response.status_code < 400:
        self.__cache(response.text)
        self.__parse_file(self._cache_file)
      else:
        self.__log("Unsupported status code received from server: %s" % response.status_code)
        result = False
        
      self.__log("load_from_url() ended")
      return result
      
    except Exception as ex:
      self.__log("Downloading resource failed! %s" % ex)
      return False


  def __cache(self, content):
    '''
    Saves the m3u locally and counts the lines
    Needed for the progress bar
    '''
    self.__log("cache() started!")
    self.__log("Saving to cache file: %s" %  self._cache_file)
    with open(self._cache_file, 'w', encoding='utf-8') as file:
      file.write(content)      
    self.__log("cache() ended!")
    
 
  def __parse_file(self, file_path):
    '''
    '''
    self.__log("__parse_file() started")
    with open(file_path, "r", encoding="utf8") as file_content:
      size = self.__count_lines(file_content)
      file_content.seek(0)
      self.__parse(file_content, size)
    
    
  def __parse(self, file_content, size):
    '''
    '''
    self.__log("__parse() started")
    
    parser = PlaylistParser(
      size = size,
      log_delegate = self.__log,
      progress_delegate = self._progress_delegate,
      progress_start = self._progress_start_value,
      progress_end = self._progress_end_value
    )
    parser.parse(file_content)
    self.streams = parser.extracted_streams
    self.__log("Parsed %s streams" % (len(self.streams)))
    self.__log("__parse() ended")
    
      
  def __count_lines(self, lines):
    i = 0
    for line in lines:
      i += 1
    return i

  
  def overwrite_values(self, map=None, remove_unmapped_streams=False):
    '''
    Overwrite stream properties with values from a JSON map
    '''
    if map: 
      self.__streams_info_map = map
      
    for stream in self.streams:
      stream_info_map = self.__streams_info_map.get_stream_info(stream.name)
      if remove_unmapped_streams and stream_info_map == {}:
        self.__log('Stream %s disabled as per addon settings' % stream.name)
        stream.disabled = True
        continue
      stream.replace_values(stream_info_map)

    
  def reorder(self, map=None):
    ''' 
    Reorders channels in the playlist
    '''
    self.__log("reorder() started") 
    if map:
      self.__streams_info_map = map
    self.__assign_stream_order_from_map()
    self.streams = sorted(self.streams, key=lambda stream:int(stream.properties['ch-order']))    
    self.__log("reorder() ended")


  def __assign_stream_order_from_map(self):
    '''
    Asigns each stream a 'ch-order' property as per the map
    '''
    percent = 95
    max = 3
    step = round(len(self.streams)/max)    
    self.__progress(percent, "Reordering playlist")
    for i, stream in enumerate(self.streams):
      if i % step == 0: 
        percent += 1
      stream.set_order(self.__streams_info_map.get_stream_order(stream.name, i))


  def add_streams(self, streams):
    ''' 
    Adds streams to playlist
    '''
    try:
      self.streams.extend(streams)
    except Exception as er:
      self.__log('Error during adding streams')
      self.__log(er, 4)

  def has_no_streams(self):
    '''
    '''
    return len(self.streams) == 0


  def __to_string(self, type):
    ''' 
      Outputs the current streams into different formats
    '''
    self.__log("__to_string() started!")
    if not type:
      type = self._type
    self.__progress(98, "Saving playlist. Type: %s" % type.name)
    
    buffer = '#EXTM3U\n'
    # percent = 0
    n = len(self.streams)
    # step = round(n/100)
    enabled_streams = 0
    
    for i in range(0, n):      
      if not self.streams[i].disabled or type == PlaylistType.NAMES or type == PlaylistType.JSON:
        stream_string = self.streams[i].to_string()
        enabled_streams += 1
        if type == PlaylistType.JSON:
          if i < (n-1): stream_string += ","
        buffer += stream_string
          
    if type == PlaylistType.JSON:
      buffer = "[%s]" % buffer
    
    self.__log("__to_string() returned %s streams" % enabled_streams)
    return buffer
    
    
  def save(self, folder_path, ouput_type = None):
    '''
    Saves current playlist into a file
    Kwargs:
      path - path to the file where the playlist will be saved. 
        If no path is given and the playlist is loaded from file 
        it will be overwritten. If no path is given and the 
        playlist is loaded from url, it will be saved in the current folder 
      type - the type of playlist
    '''
    
    self.__serialize()

    if not folder_path:
      raise Exception('No path provided to save the playlist')

    if not ouput_type:
      ouput_type = self._type
      
    try:
      file_path = os.path.join(folder_path, self.name)
      with open(file_path, 'w', encoding="utf8") as file:
        self.__log("Saving playlist type %s in %s " % (self._type, file_path))
        file.write(self.__to_string(self._type))        
      return True
    
    except Exception as er:
      self.__log_exception()
      return False

    
  def __serialize(self):
    '''
    Serializes streams dict into a file so it can be used later
    '''
    self.__log("__serialize() started")
    self.__progress(80, "Serializing streams")
          
    PlaylistSerializer(
      self._temp_folder,
      log_delegate=self.__log
      ).serialize(self.streams)

    self.__log("__serialize() ended")

    
  def __log(self, msg):
    if self._log_delegate:
      self._log_delegate(msg) 


  def __log_exception(self):
    import traceback
    msg = traceback.format_exc(sys.exc_info())
    self.__log(msg, 4)
    
  
  def __progress(self, percent, msg):
    if self._progress_delegate:
      self._progress_delegate.update(percent, str(msg))
      