# -*- coding: utf-8 -*-
from .utils import *
from urllib.parse import unquote
from bottle import route, request, HTTPResponse, default_app
from .notifications import notify_error
from .playlist_serializer import PlaylistSerializer

GET  = 'GET'
HEAD = 'HEAD'
app  = default_app()

@route('/playlist', method=GET)
def get_playlist():
  '''
    Displays the m3u playlist
    :return: m3u
  '''
  log_error('get_playlist() started')
  body = '#EXTM3U\n'
  try:
    pl_path = os.path.join(profile_path, 'playlist.m3u')
    with open(pl_path, 'r', encoding='utf8') as file:
      body = file.read() 
      
  except Exception as er:
    log_error(body)

  headers = {}
  
  if request.query.get('debug') != None:
    body = '<pre>' + unquote(body) + '</pre>'
  else:
    headers['Content-Type'] = 'audio/mpegurl'
    
  log_info('get_playlist() ended')
  
  return HTTPResponse(body, status=200, **headers)


@route('/stream/<name>', method=HEAD)
def get_stream(name):
  return HTTPResponse(None, status=200)


@route('/stream/<name>', method=GET)
def get_stream(name):
  '''
    Get the m3u stream url
    Returns 302 redirect
  '''
  headers  = {}
  body     = None
  location = None
  log_info("get_stream() started")

  try:  
    streams = PlaylistSerializer(
      profile_path,
      # log_delegate=log
      ).deserialize()
    
    stream_name = unquote(name)
    location = streams.get(stream_name)

    if request.query.get('debug') != None:
      return HTTPResponse(location, status = 200)
    log_info(location)
    
    if not location:
      notify_error('Unable to find stream for %s' % name)
      return HTTPResponse(body, status = 404)
                      
    headers['Location'] = location

  except Exception as ex:
    return HTTPResponse(ex, status=500, **headers)
    
  log_info("get_stream() ended!")
  return HTTPResponse(body, status = 302, **headers)
