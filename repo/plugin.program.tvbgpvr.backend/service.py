from xbmc import executebuiltin, Monitor
from resources.lib.server import create_server
from resources.lib.wsgi_app import *
from resources.lib.utils import *

executebuiltin(RUNSCRIPT)
monitor = Monitor()

httpd = create_server(BIND_IP, app, port=port)
httpd.timeout = 0.1
starting = True

while not monitor.abortRequested():
  httpd.handle_request()
  if starting:
    notify(translate(32006) % port)
    starting = False

httpd.socket.close()
settings.first_request = False
log(translate(32003))