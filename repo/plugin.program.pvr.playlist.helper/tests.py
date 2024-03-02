import os
from pathlib import Path
import unittest

from resources.lib.stream import Stream
from resources.lib.enums import *
from resources.lib.m3u_parser import PlaylistParser  
from resources.lib.map import StreamsMap
from resources.lib.playlist import Playlist
    
user_temp_folder = os.environ.get('temp')
current_file_dir = Path(__file__).resolve()

class Tests(unittest.TestCase):
    
  ####################
  ### Stream tests ###
  ####################

  def test_parse_line(self):
    """
      Tests if Stream.parse method parses m3u line correctly
    """
    stream = Stream(
      #, log_delegate=print
    )
    stream.parse('#EXTINF:-1 tvg-id="tivi.id" tvg-name="tivi.id" group-title="information" \
     catchup="default" catchup-source="http://url?lutc=${timestamp}" catchup-days="7" ch-number="1" \
       tvg-chno="1" channel-id="1" ch-order="1",Channel 1')
    
    self.assertEqual(stream.name, 'Channel 1')
    self.assertEqual(stream.properties['tvg-id'], 'tivi.id')
    self.assertEqual(stream.properties['tvg-name'], 'tivi.id')
    self.assertEqual(stream.properties['group-title'], 'information')
    self.assertEqual(stream.properties['ch-number'], '1')
    self.assertEqual(stream.properties['tvg-chno'], '1')  
    self.assertEqual(stream.properties['channel-id'], '1')  
    self.assertEqual(stream.properties['ch-order'], '1')
    self.assertEqual(stream.properties['catchup'], 'default')
    self.assertEqual(stream.properties['catchup-source'], 'http://url?lutc=${timestamp}')
    self.assertEqual(stream.properties['catchup-days'], '7')


  def test_to_string(self):
    '''
      Tests if stream.to_string method exports all properties
    '''
    stream = Stream()
    stream.name = "Channel 1"
    stream.properties['group-title'] = 'MyGroup'
    stream.properties['tvg-id'] = 'tivi.id'
    stream.properties['tvg-name'] = 'tivi.id'
    stream.properties['catchup'] = 'default'
    stream.properties['catchup-source'] = 'http://url?lutc=${timestamp}'
    stream.properties['catchup-days'] = '7'
    stream.properties['ch-number'] = '7'
    stream.properties['tvg-chno'] = '7'
    stream.properties['ch-order'] = '7'
    
    stream_as_string = stream.to_string()

    self.assertTrue(stream_as_string.startswith('#EXTINF:-1'))
    self.assertTrue(',' + stream.name in stream_as_string)
    self.assertTrue('group-title="MyGroup"' in stream_as_string)
    self.assertTrue('tvg-id="tivi.id"' in stream_as_string)
    self.assertTrue('tvg-name="tivi.id"' in stream_as_string)
    self.assertTrue('tvg-chno="7"' in stream_as_string)
    self.assertTrue('ch-number="7' in stream_as_string)
    self.assertTrue('ch-order="7' in stream_as_string)
    self.assertTrue('catchup-source="http://url?lutc=${timestamp}"' in stream_as_string)


  def test_to_string_with_modified_order(self):
    '''
      Tests if stream.to_string method changes the ch-order and tvg-chno attributes when order is true
    '''
    stream = Stream()
    stream.name = "Channel 1"
    stream.properties['tvg-chno'] = '7'
    stream.properties['ch-order'] = '7'
    stream.set_order(1)

    _stream_as_string = stream.to_string()
    
    self.assertTrue('tvg-chno="1"' in _stream_as_string)
    self.assertTrue('ch-order="1"' in _stream_as_string)

    
  def test_parse_line_with_values_with_spaces(self):
    '''
      Property values with spaces should be parsed no issues
    '''
    stream = Stream(
      #log_delegate=print
      )
    stream.parse('#EXTINF:-1 group-title="Low bandwidth" , Channel 1 +24 HD')

    self.assertEqual(stream.name, 'Channel 1 +24 HD')
    self.assertEqual(stream.properties['group-title'], 'Low bandwidth')


  def test_parse_line_with_stream_name_with_more_commas(self):
    '''
      Channel name containig a comma is parsed correctly and the comma is replaced
    '''
    stream = Stream(
      #, log_delegate=print
    )
    stream.parse('#EXTINF:-1,Channel 1, DE & EU')

    self.assertEqual(stream.name, 'Channel 1 DE & EU')


  def test_stream_replace_values(self):
    '''
      Stream properties are replaced with their match from the streams map
    '''
    stream = Stream()
    stream.name = "Channel 1"
    stream.properties['group-title'] = 'MyGroup'
    stream.properties['tvg-id'] = 'tivi.id'
    stream.properties['ch-number'] = '7'
    stream.properties['tvg-chno'] = '7'
    stream.properties['ch-order'] = '7'

    stream.replace_values({'tvg-id':'tivi.222', 'tvg-name':'Channel 1 HD', 'group-title':'information','tvg-chno':'1'})

    self.assertEqual(stream.name, "Channel 1")
    self.assertEqual(stream.properties['tvg-name'], "Channel 1 HD")
    self.assertEqual(stream.properties['tvg-id'], "tivi.222")
    self.assertEqual(stream.properties['group-title'], "information")
    self.assertEqual(stream.properties['tvg-chno'], '1')


  # ############################
  # ### Channel Tests ###
  # ############################
  # def test_create_channel_from_stream(self):
  #   """
  #   Test channel object creation
  #   """
  #   stream = Stream('#EXTINF:-1 tvg-id="tivi.id" tvg-name="tivi.id" group-title="information" ch-number="1" tvg-chno="1" channel-id="1" ch-order="1",CHANNEL1 HD +24', streams_map=streams_map, groups_map=groups_map, groups_from_progider=False) #log=print, 
  #   channel = Channel(stream)
    
  #   self.assertEqual(channel.id, stream.channel_id)
  #   self.assertEqual(len(channel.streams), 1)    
    
  
  # ############################
  # ### PlaylistParser Tests ###
  # ############################
  
  def test_playlistparser_parses(self):
    """
    Test playlist parser parses lines containing a single stream
    """
    content = ['#EXTINF:-1 tvg-id="tivi.id" tvg-name="tivi.id" group-title="High Definition" ch-number="1" \
     tvg-chno="1" channel-id="1" ch-order="1",Channel 1 HD',
     '#EXTSIZE: medium', 
     'http://url?stid=1&mac=AA:BB:CC:DD:FF:EE&key=123456&stb=&codec=']
    
    parser = PlaylistParser(
      #log_delegate=print
    )
    parser.parse(content)

    self.assertEqual(len(parser.extracted_streams), 1)
    self.assertEqual(parser.extracted_streams[0].properties['tvg-id'], 'tivi.id')
    self.assertEqual(parser.extracted_streams[0].properties['group-title'], 'High Definition')
    self.assertEqual(parser.extracted_streams[0].name, 'Channel 1 HD')
    self.assertEqual(parser.extracted_streams[0].url, 'http://url?stid=1&mac=AA:BB:CC:DD:FF:EE&key=123456&stb=&codec=')
    
    self.assertTrue('tvg-id="tivi.id"' in parser.extracted_streams[0].to_string())
    self.assertTrue(',Channel 1 HD' in parser.extracted_streams[0].to_string())
    self.assertTrue('group-title="High Definition"' in parser.extracted_streams[0].to_string())
    self.assertTrue('http://url' in parser.extracted_streams[0].to_string())


  # ############################
  # ###   StreamsMap Tests  ###
  # ############################
  
  def test_streams_map_load_from_file(self):
    
    map = StreamsMap(path=os.path.join(current_file_dir.parent, '..\\map.json'))
    map2 = StreamsMap()
    map2.load_map(os.path.join(current_file_dir.parent, '..\\map.json'))
    
    self.assertNotEqual(map, None)
    self.assertNotEqual(map2, None)
    
    self.assertEqual(map.get_stream_info('NatGeo HD'), map2.get_stream_info('NatGeo HD'))


  def test_streams_map_load_from_url(self):
    
    map = StreamsMap(path='https://raw.githubusercontent.com/harrygg/EPG/master/maps/map.json')
    map2 = StreamsMap()
    map2.load_map('https://raw.githubusercontent.com/harrygg/EPG/master/maps/map.json')
    
    self.assertNotEqual(map, None)
    self.assertNotEqual(map2, None)


  def test_streams_map_have_order_attribute(self):
        
    map = StreamsMap(map={'Channel 1': {},'Channel 2': {}})
    
    self.assertEqual(map.get_stream_info('Channel 1')['order'], 1)
    self.assertEqual(map.get_stream_info('Channel 2')['order'], 2)
    
  # ############################
  # ### PlaylistParser Tests ###
  # ############################
  
  def test_playlist(self):
    '''
    '''   
    map = StreamsMap(path=os.path.join(current_file_dir.parent, '..\\map.json'))
    playlist = Playlist(
      # log_delegate=print,
      temp_folder=user_temp_folder,
      map=map
    )
    playlist.load_from_file(os.path.join(os.path.expanduser("~"), 'Downloads', 'playlist.m3u'))
    playlist.overwrite_values()
    playlist.save(os.path.join(user_temp_folder, 'playlist.m3u'))

    self.assertEqual(len(playlist.streams), 677)
    self.assertEqual(playlist.streams[3].properties['tvg-chno'], '4')   


  
  def test_playlist_reorder(self):
    '''
      Tests that streams are ordered by the order in map.
      If stream is not in map it is put after all streams in the map.
    '''
    playlist = Playlist()

    playlist.streams = [
      Stream(name='Channel 1'),
      Stream(name='Channel 3'),
      Stream(name='Channel 4'),
      Stream(name='Channel 2'),
      Stream(name='Channel 5')
    ]

    map = StreamsMap(map={'Channel 1': {},'Channel 2': {},'Channel 5': {}})
    playlist.reorder(map)

    self.assertEqual(playlist.streams[0].name, 'Channel 1')
    self.assertEqual(playlist.streams[1].name, 'Channel 2')
    self.assertEqual(playlist.streams[2].name, 'Channel 5')
    self.assertEqual(playlist.streams[3].name, 'Channel 3')
    self.assertEqual(playlist.streams[4].name, 'Channel 4')


if __name__ == '__main__':
    unittest.main()