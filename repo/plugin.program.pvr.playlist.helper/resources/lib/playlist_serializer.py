import os
import json

class PlaylistSerializer():
    '''
    '''
    def __init__(self, folder, **kwargs):
        self._folder = folder
        self._name = kwargs.get('file_name', '.streams')
        self._log_delegate = kwargs.get('log_delegate')
        self._path = os.path.join(self._folder, self._name) if self._folder else self._name

    def serialize(self, streams):
        '''
        '''
        self.__log("Serializing %s streams in %s" % (len(streams), self._path))
        _streams = {}
        for stream in streams:
            _streams[stream.name] = stream.url        
        with open(self._path, "w", encoding="utf8") as w:
          w.write(json.dumps(_streams, ensure_ascii=False))
        
    def deserialize(self):
        '''
        '''
        try:
            # self.__log("Desrializing streams from file %s" % (self._path))
            _streams = json.load(open(self._path, encoding='utf-8'))
        except Exception as ex:
            self.__log(ex)
        return _streams
    
    def __log(self, msg):
        if self._log_delegate:
            self._log_delegate(msg) 