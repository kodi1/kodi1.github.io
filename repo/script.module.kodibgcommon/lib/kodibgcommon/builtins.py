import xbmc

def AlarmClock(name, script, interval, isSilent=True, loop=False):
  '''
  Executes the builtin AlarmClock function
  '''
  params = "'%s', %s, %s" % (name, script, interval)

  if isSilent:
    params += ", silent"
  
  if loop:
    params += ", loop"
    
  command = "AlarmClock(%s)" % params
  xbmc.executebuiltin(command)
  
  
  
