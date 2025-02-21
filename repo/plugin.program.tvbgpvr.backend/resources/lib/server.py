from wsgiref.simple_server import ServerHandler, WSGIServer, WSGIRequestHandler, make_server
from SocketServer import ThreadingMixIn

class SilentWSGIRequestHandler(WSGIRequestHandler):
  """Custom WSGI Request Handler with logging disabled"""
  protocol_version = 'HTTP/1.1'

  def log_message(self, *args, **kwargs):
    """Disable log messages"""
    pass


class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
  """Multi-threaded WSGI server"""
  allow_reuse_address = True
  daemon_threads = True


def create_server(ip, app, port=18910):
  """
  Create a new WSGI server listening on 'port' for WSGI app
  """
  ServerHandler.http_version = '1.1'
  ServerHandler.server_software = "TVBGPVR.BACKEND"

  return make_server(ip, port, app,
                     server_class=ThreadedWSGIServer,
                     handler_class=SilentWSGIRequestHandler)
