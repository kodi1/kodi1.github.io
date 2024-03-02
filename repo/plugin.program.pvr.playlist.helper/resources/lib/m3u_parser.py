from .stream import Stream
  
class PlaylistParser:
  '''
  '''
  
  def __init__(self, **kwargs):
    '''
    '''
    self.extracted_streams = []
    self._log_delegate = kwargs.get('log_delegate', None)
    self._progress_delegate = kwargs.get('progress_delegate', None)
    self._current_progress = kwargs.get('progress_start', 10)
    max_percent = kwargs.get('progress_end', 80)
    lines_count = kwargs.get('size', 0)
    self._progress_step = round(lines_count/max_percent) if lines_count > 0 else 16
    
    
  def parse(self, lines):
    ''' 
      Parse m3u file line by line. Usually the stream information is spread accross multiple lines.
      First is #EXTINF, then maybe #EXTSIZE and others and the last line contains the stream URL.
      So we create a stream object and add the extracted stream details. Then we add the stream to an exisiting or a new channel.
      After a stream url is added, the stream object is appended to the streams list and reset.
    '''
    self.__log("PlaylistParser.parse() started!")
    stream = None

    for i, line in enumerate(lines):
      self.__update_progress_bar(i, "Parsing playlist")      

      line = line.rstrip()
      if line and line.startswith("#EXTM3U") or line.startswith("#EXTSIZE"):
        continue

      if line.startswith("#EXTINF"):
        stream = self.__create_stream(line)
      else:
        if stream is None:
          continue
        stream.url = line
        self.extracted_streams.append(stream)
        self.__log("Adding stream to playlist %s" % stream.name)

    self.__log("PlaylistParser.parse() ended")
    
    
  def __create_stream(self, line):
    '''
      Factory method to create stream object with the required details
    '''
    try:
      stream = Stream(
        log_delegate=self.__log
      )
      stream.parse(line)
      return stream
    except Exception as ex:
      self.__log("Exception during stream creation. %s. Skipping stream" % ex)
      return None


      
  def __update_progress_bar(self, i, msg):
    '''
      __update_progress_bar: updates the progress bar given the current line number and message
      :param i: the current line number
      :param msg: the message that will be displayed in the progress bar
    '''
    if self._progress_delegate is None:
      return

    if i % self._progress_step == 0: 
      self._current_progress += 1      
      self._progress_delegate.update(self._current_progress, str(msg))

            
  def __log(self, msg):
    if self._log_delegate:
      self._log_delegate(msg)      
      
      