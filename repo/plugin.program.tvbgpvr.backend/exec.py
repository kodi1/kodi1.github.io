# -*- coding: utf-8 -*-
import os
import xbmc
import urllib
import xbmcgui
from resources.lib.utils import *
from resources.lib.playlist import *

#append_pydev_remote_debugger
# if os.environ.get('TVBGPVRDEBUG'):
  # sys.path.append(os.environ['PYSRC'])
  # import pydevd
  # pydevd.settrace('127.0.0.1', stdoutToServer=False, stderrToServer=False)
#end_append_pydev_remote_debugger	

log("Addon running on: %s" % user_agent)
if scheduled_run:
  log(translate(32004))
  
### If addon is started manually or is in debug mode, display the progress bar 
if not scheduled_run or settings.debug:
  progress_bar = xbmcgui.DialogProgressBG()
  progress_bar.create(heading=this.getAddonInfo('name'))

try:
  # Initialize the playlsit object
  pl = Playlist(location=get_location(),
                user_agent=user_agent, 
                progress=progress_bar,
                temp_folder=profile_dir,
                disabled_groups=get_disabled_groups(),
                mapping_file=mapping_file)
  
  if pl.count() == 0:
    notify_error(translate(32000))
  else:
    ### If there is a preferred quality for channels with multi streams, 
    ### remove all unpreferred streams
    if (settings.preferred_quality != ALL):
      pl.set_preferred_quality(settings.preferred_quality)

    ### Reorder playlist as per the order in the template file
    pl.reorder(template_file=get_template_file())
    
    ### Replace stream URLs with static ones
    pl.set_static_stream_urls(STREAM_URL)

    ### Export channel names from original playlist
    if settings.export_names:
      names_file_path = os.path.join(settings.export_to_folder, "names.txt")
      pl.save(path=names_file_path, type=PlaylistType.NAMES)
      # Export channel names & ids from original playlist
      # Needed only for the EPG generation. Users can disable it!!!
      names_file_path = os.path.join(settings.export_to_folder, "channels.json")
      pl.save(path=names_file_path, type=PlaylistType.JSON)
              
    ### Write playlist to disk
    if not pl.save(path=pl_path):
      notify_error(translate(32001))

    ### Copy playlist to additional folder if specified
    if settings.copy_playlist and os.path.isdir(settings.copy_to_folder):
      pl.save(path=os.path.join(settings.copy_to_folder, pl_name))

except Exception, er:
  log(er, xbmc.LOGERROR)

### Schedule next run
interval = int(settings.run_on_interval) * 60
log(translate(32007) % interval)
command = "AlarmClock('ScheduledReload', %s, %s, silent)" % (RUNSCRIPT, interval)
xbmc.executebuiltin(command)

if progress_bar:
  progress_bar.close()
