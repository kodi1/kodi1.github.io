# -*- coding: utf-8 -*-
import os
import re
import requests
from .utils import *
from urllib.parse import unquote
from .bottle import route, default_app, request, HTTPResponse

__DEBUG__ = os.environ.get('TVBGPVRDEBUG')
app       = default_app()
port      = settings.port

@route('/playlist', method=GET)
@route('/tvbgpvr.backend/playlist', method=GET)
def get_playlist():
  """
    Displays the m3u playlist
    :return: m3u
  """
  log("get_playlist() started")
  body = "#EXTM3U\n"
  try:
    with open(pl_path) as file:
      body = file.read()

  except Exception as er:
    body = str(er)
    log(str(er))

  headers = {}

  #explicitly check for None as it could be empty value
  if request.query.get("debug") != None:
    body = "<pre>" + body + "</pre>"

  else:
    headers['Content-Type'] = "audio/mpegurl"

  log("get_playlist() ended")

  return HTTPResponse(body,
                      status=200,
                      **headers)


@route('/stream/<name>', method=HEAD)
@route('/tvbgpvr.backend/stream/<name>', method=HEAD)
def get_stream(name):
  return HTTPResponse(None,
                      status=200)


@route('/stream/<name>', method=GET)
@route('/tvbgpvr.backend/stream/<name>', method=GET)
def get_stream(name):
  '''
    Get the m3u stream url
    Returns 302 redirect
  '''

  headers  = {}
  body     = None
  location = None

  if request.query.get("debug") != None:
    stream_name = unquote(name)
    location = get_stream_url(stream_name)
    return HTTPResponse(location, status = 200)

  log("get_stream() started.")
  log("User-agent header: %s" % request.headers.get("User-Agent"))
  try:
    is_tvheadend = "TVHeadend" in request.headers.get("User-Agent")
  except:
    is_tvheaded = False
  ### Kodi 17 sends 2 GET requests for a resource which may cause
  ### stream invalidation on some middleware servers. If this is
  ### the first request return a dummy response and handle the 2nd
  log("Is TV Headned: %s" % is_tvheadend)
  if not is_tvheadend and VERSION > 16 and not settings.first_request_sent:

    settings.first_request_sent = True
    log("get_stream() ended. First request handled!")
    return HTTPResponse(body,
                      status = 200,
                      **headers)

  ### If this is the 2nd request by the player
  ### redirect it to the original stream
  settings.first_request_sent = False

  try:
    stream_name = unquote(name)
    location = get_stream_url(stream_name)

    if not location:
      notify_error(translate(32008) % name)
      return HTTPResponse(body,
                          status = 404)

    if __DEBUG__:
      notify("URL found for stream %s: %s" % (stream_name, location))
      log("get_stream() ended!")
      return HTTPResponse(location,
                          status = 200)

    headers['Location'] = location

  except Exception as er:
    body = str(er)
    log(str(er), 4)

  log("get_stream() ended!")
  return HTTPResponse(body,
                      status = 302,
                      **headers)
