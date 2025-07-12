import time

import xbmc

from resources.lib.helper import Helper
from resources.lib.sweettv import refreshToken, initSettings, refreshChannelList

if __name__ == '__main__':
    monitor = xbmc.Monitor()
    helper = Helper()
    refreshChannelListTimer = 0
    initSettings()

    while not monitor.abortRequested():
        try:
            refreshToken()

            if int(time.time()) - refreshChannelListTimer > 15 * 60:
                refreshChannelList()
                refreshChannelListTimer = int(time.time())

            if monitor.waitForAbort(60):
                break
        except Exception as e:
            xbmc.log("Service exception: " + str(e), xbmc.LOGERROR)
