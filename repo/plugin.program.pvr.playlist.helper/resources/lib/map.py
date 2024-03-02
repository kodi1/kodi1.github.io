import json
import requests

class StreamsMap:
    
    def __init__(self, **kwargs):
        self.__log_delegate = kwargs.get('log_delegate', None)
        self.__log('Creating StreamsMap object')
        self.__path = kwargs.get('path', None)
        self.__map = kwargs.get('map', {})
        if self.__path:
            self.load_map(self.__path)
        if self.__map is not {}:
            self.__calculate_streams_order()
        

    def get_stream_info(self, stream_name):
        '''
        Returns the stream information or a default dict object 
        '''
        return self.__map.get(stream_name, {})


    def get_stream_order(self, stream_name, current_index):
        '''
        Returns the order of a stream if present, else the current_index plus the length of all streams
        '''
        stream_info = self.__map.get(stream_name, {})
        order = stream_info.get('ch-order', None)
        if order is not None:
            self.__log('Setting order of stream %s to %s' % (stream_name, order))
            return order
        else:
            offset = current_index + len(self.__map)
            self.__log('Offsetting order of stream %s to %s' % (stream_name, offset))
        return offset


    def load_map(self, map_location):
        '''
        Downloads or open and parse the streams map file.
        '''
        self.__log('Loading map from location: %s' % map_location)
        try:
            if 'http' in map_location or 'ftp' in map_location:
                self.__map = self.__download_map(map_location)
            else:
                with open(map_location, encoding='utf8') as map_content:
                    self.__map = json.load(map_content)
        except Exception as ex:
            self.__log('Loading map failed! %s' % ex)

        self.__log("Loaded streams map contains %s" % len(self.__map))
        return self.__map
        

    def __download_map(self, map_location):
        '''
        Downloads map file, returns the parsed JSON
        '''
        headers = {"Accept-Encoding": "gzip, deflate"}
        response = requests.get(map_location, headers=headers)
        self.__log("Map server status code: %s " % response.status_code)
        self.__log("Map size: %s " % response.headers.get('Content-Length', None))
        if response.status_code < 200 and response.status_code >= 400:
            raise Exception("Unsupported status code!")        
        return response.json()

    
    def __calculate_streams_order(self):
        '''
        Assign an order property to each map item
        '''
        for i, stream_details in enumerate(self.__map.values()):
            stream_details['ch-order'] = i + 1


    def __log(self, msg):
        if self.__log_delegate:
            self.__log_delegate(msg)
    