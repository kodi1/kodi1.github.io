from wsgiref.simple_server import ServerHandler, WSGIServer, WSGIRequestHandler, make_server
from socketserver import ThreadingMixIn
from .wsgi_app import app

class SilentWSGIRequestHandler(WSGIRequestHandler):
  """Custom WSGI Request Handler with logging disabled"""
  protocol_version = 'HTTP/1.1'

  def log_message(self, *args, **kwargs):
    """Disable log messages"""
    pass


class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
  allow_reuse_address = True
  daemon_threads = True


def create_server(ip, port):
  ServerHandler.http_version = '1.1'
  ServerHandler.server_software = id
  return make_server(ip, port,  app,
                     server_class=ThreadedWSGIServer,
                     handler_class=SilentWSGIRequestHandler)
