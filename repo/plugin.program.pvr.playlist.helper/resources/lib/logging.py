import xbmc
from .addon import *

def log(msg, level=xbmc.LOGINFO):
  try:
    xbmc.log("%s v%s | %s" % (id, addon_version, msg), level)
  except Exception as ex:
    xbmc.log(ex)


def log_info(msg):
  log(msg, xbmc.LOGINFO)


def log_error(msg):
  log(msg, xbmc.LOGERROR)


def log_last_exception():
  log_error(get_last_exception())
  
  
def get_last_exception():
  import sys, traceback
  traceback.format_exc(sys.exc_info())