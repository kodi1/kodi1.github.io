# -*- coding: utf8 -*-
import re
import json
import urllib
from .enums import StreamQuality, PlaylistType


class Stream:
  '''
    Class definition for m3u stream entries
  '''

  def __init__(self, **kwargs):
    '''
    '''
    self.name           = kwargs.get('name', None)
    self.properties     = kwargs.get('properties', {})
    self.static_url     = kwargs.get('static_url_template', 'http://127.0.0.1:18910/stream/%s')
    self.url            = kwargs.get('url', None)
    self.disabled       = False
    self._log_delegate  = kwargs.get('log_delegate', None)
    self._ordinal       = kwargs.get('ordinal', -1)
    self._line          = None


  def parse(self, line):
    '''
      Parse a playlist line that starts with #EXTINF and extracts the stream name and all key=value pairs 
    '''
    if not line.startswith('#EXTINF'):
      raise Exception('Parsed line must start with #EXTINF %s' % line)
    self._line = line

    matches = line.split(',')
    self.__extract_name(matches)

    line = matches[0].replace('#EXTINF:-1', '').strip()

    valuepairs = re.compile(r'\s*(.*?)=[\'"]+(.*?)[\'"]+\s*').findall(line)
    self.__parse_valuepairs(valuepairs) #[1:])


  def replace_values(self, map):
    '''
      Replaces the existing property values with the new values from the provided map
    '''
    if map == {}:
      self.__log('No stream info provided for stream %s.' % self.name)
      return

    self.__log('Stream info provided for stream %s %s' % (self.name, map))
    for key, value in map.items():
      self.properties[key] = value

    self.disabled = self.properties.get('disabled', False)
      

  def __extract_name(self, matches):
    '''
    '''
    if len(matches) == 0:
      raise Exception('Unable to extract sream name from line %s' % self._line)
    elif len(matches) > 1:
      self.name = "".join(matches[1:]) # In case stream name contains a comma
    else:
      self.name = matches[1]
    self.name = self.name.strip()
    self.__log('Extracted stream name %s' % self.name)


  def __parse_valuepairs(self, valuepairs):
    '''
    '''
    if len(valuepairs) == 0:
      self.__log('No properties extracted from line %s' % self._line)
      return
    
    for valuepair in valuepairs:
      if len(valuepair) == 1:
        self.__log("Missing value in keyvalue pair. Skipping it")
        continue
      self.properties[valuepair[0]] = valuepair[1].strip('"\'')
      self.__log('Extracted property %s with value %s' % (valuepair[0], self.properties[valuepair[0]]))


  def set_order(self, order):
    '''
    '''
    self.__log('Setting order of stream %s to %s' % (self.name, order))
    self.properties['tvg-chno'] = order
    self.properties['ch-order'] = order
        

  def to_string(self, type=PlaylistType.KODIPVR, static_url=True):
    '''
      Exports the stream to string, that is 2 lines - the #EXTINFO line and the stream URL line 
    '''     
    buffer = '#EXTINF:-1'
    
    if type is not PlaylistType.PLAIN:
      for key in self.properties:
        buffer += ' %s="%s"'  % (key, self.properties[key])
    
    url = self.get_static_url() if static_url else self.url
    buffer += ',%s\n%s\n' % (self.name, url)

    return buffer
  
  
  def get_static_url(self):
    name = urllib.parse.quote(self.name)
    return self.static_url % name
  
    
  def __log(self, msg):
    if self._log_delegate :
      self._log_delegate (msg)  
      

  def to_json(self):
    '''
      Outputs the stream object into a JSON formatted string
    '''
    return json.dumps({self}, ensure_ascii=False)