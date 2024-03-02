# -*- coding: utf-8 -*-
from xbmcgui import DialogProgressBG
from resources.lib.utils import *
from resources.lib.settings import settings 
from resources.lib.utils import addon, profile_path
from resources.lib.notifications import notify_error

# import web_pdb; web_pdb.set_trace()

progress_bar = None
if is_manual_run() or settings.debug:
  progress_bar = DialogProgressBG()
  progress_bar.create(heading=addon_name)

try:
  playlist = PlaylistFactory.create(progress_delegate=progress_bar)
  m3u_location = settings.m3u_path if settings.m3u_path_type == 0 else settings.m3u_url
  playlist.load(m3u_location)

  if settings.concat_second_playlist:
    playlist2 = PlaylistFactory.create(progress_delegate=progress_bar)
    m3u2_location = settings.m3u2_path if settings.m3u2_path_type == 0 else settings.m3u2_url
    playlist2.load(m3u2_location)
    playlist.add_streams(playlist2.streams)
  playlist.overwrite_values(streamsmap, remove_unmapped_streams=settings.only_streams_from_map)

  if playlist.has_no_streams():
    notify_error('The playlist has NO channels!')  
  else:
    if settings.reorder_playlist:
      playlist.reorder()

    if not playlist.save(profile_path):
      notify_error('The playlist was NOT saved!')

    if settings.copy_playlist and os.path.isdir(settings.copy_to_folder):
      playlist.save(os.path.join(settings.copy_to_folder))

except Exception as er:
  log_last_exception()

if settings.m3u_refresh_mode > 0:
  schedule_next_run(settings.m3u_refresh_interval_mins)

if progress_bar:
  progress_bar.close()
