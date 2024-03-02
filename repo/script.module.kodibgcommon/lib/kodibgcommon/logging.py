import xbmc
from .settings import Settings
from .utils import get_addon_id, get_addon_version, get_addon_version, get_last_exception, get_kodi_version, get_platform

settings = Settings()

def log_info(msg):
  log(msg, xbmc.LOGINFO)


def log_error(msg):
  log(msg, xbmc.LOGERROR)


def log_debug(msg):
  log(msg, xbmc.LOGDEBUG)


def log_last_exception():
  log_error(get_last_exception())


def log_kodi_platform_version():
  """
  Log our Kodi version and platform for debugging
  """
  version = get_kodi_version()
  platform = get_platform()
  log_info("Kodi %s running on %s" % (version, platform))
  

def log(msg, level=xbmc.LOGDEBUG):
  try:
    if settings.debug and level == xbmc.LOGDEBUG:
      level = xbmc.LOGINFO
    xbmc.log("%s v%s | %s" % (get_addon_id(), get_addon_version(), str(msg)), level)
  except:
    pass
