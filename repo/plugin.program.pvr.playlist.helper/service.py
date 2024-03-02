from xbmc import executebuiltin, Monitor
from resources.lib.utils import *
from resources.lib.server import create_server
from resources.lib.notifications import  notify_success
from resources.lib.settings import settings

ip   = '0.0.0.0' if settings.bind_all else '127.0.0.1'
port = settings.port

executebuiltin(RUNSCRIPT)

http_server = create_server(ip, port)
http_server.timeout = 0.1
starting = True

monitor = Monitor()
while not monitor.abortRequested():
  http_server.handle_request()
  if starting:
    notify_success('PVR.BACKEND.HELPER started on port %s' % port)
    log_info('Started PVR.BACKEND.HELPER server %s:%s' % (ip, port))
    starting = False

http_server.socket.close()
log_info('PVR.BACKEND.HELPER successfully stopped')