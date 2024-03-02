import xbmcaddon

__addon__ = xbmcaddon.Addon()

class Settings():
  ''' 
    Class for getting and setting options in kodi settings.xml file
    Usage:
    The following gets a setting called debug. If the setting does not exist it will return False:
    debug = setting.debug
    The following example sets the setting's value
    setting.debug = True
  '''
  def __getattr__(self, name):
    temp = __addon__.getSetting(name)
    if temp.lower() == 'true':
      return True
    elif temp.lower() == 'false':
      return False
    elif temp.isdigit():
      return int(temp)
    else:
      return temp
 
  def __setattr__(self, name, value):
    __addon__.setSetting(name, str(value))
    
  def open(self):
    __addon__.openSettings()

settings = Settings()