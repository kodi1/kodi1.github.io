import xbmc

def notify_error(msg, duration=5000, icon="DefaultFolder.png"):
  Notification("Error", msg, icon)
  
def notify_success(msg, duration=5000, icon="DefaultFolder.png"):
  Notification("Success", msg, icon)

def Notification(title, msg, duration=5000, icon="DefaultFolder.png"):
  '''
  Will display a notification dialog with the specified header and message, 
  in addition you can set the length of time it displays in milliseconds and a icon image
  '''
  xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % (title, msg, duration, icon))