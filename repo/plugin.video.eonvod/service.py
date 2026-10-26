import json
import threading
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

addon = xbmcaddon.Addon()

ADDON_ID = addon.getAddonInfo("id") or "plugin.video.eonvod"

ADDON_DATA = xbmcvfs.translatePath(addon.getAddonInfo("profile") or
                                   "special://profile/addon_data/%s/" % ADDON_ID)
if not ADDON_DATA.endswith("/"):
    ADDON_DATA += "/"

HOME_WINDOW = 10000

PLAYING_PROPERTY = "eonvod.playing"
PLAYING_SERIES_PROPERTY = "eonvod.playing.series"
PLAYING_SEASON_PROPERTY = "eonvod.playing.season"

CACHE_FILE = ADDON_DATA + "vod_cache.json"

SYNC_STATE_FILE = ADDON_DATA + "sync_state.json"

PLAYBACK_FILE = ADDON_DATA + "playback.json"

CACHE_VERSION = 1

RESUME_MIN_SECONDS = 60
RESUME_DONE_FRACTION = 0.90


def log(message, level=xbmc.LOGINFO):
    for line in str(message).splitlines() or [""]:
        xbmc.log(f"[{ADDON_ID}.service] {line}", level)


def lang():
    return addon.getSetting("metadata_language") or "eng"


def read_json(path, fallback):
    if not xbmcvfs.exists(path):
        return fallback
    handle = None
    try:
        handle = xbmcvfs.File(path, "r")
        data = json.loads(handle.read() or "null")
        return data if data is not None else fallback
    except Exception as exc:
        log(f"Could not read {path}: {exc}", xbmc.LOGWARNING)
        return fallback
    finally:
        if handle is not None:
            handle.close()


def write_json(path, payload):
    temporary = path + ".part"
    handle = None
    try:
        if not xbmcvfs.exists(ADDON_DATA):
            xbmcvfs.mkdirs(ADDON_DATA)
        handle = xbmcvfs.File(temporary, "w")
        handle.write(json.dumps(payload, ensure_ascii=False))
        handle.close()
        handle = None

        if xbmc.getCondVisibility("System.Platform.Windows") and xbmcvfs.exists(path):
            xbmcvfs.delete(path)
        if not xbmcvfs.rename(temporary, path):
            if xbmcvfs.exists(path):
                xbmcvfs.delete(path)
            if not xbmcvfs.rename(temporary, path):
                xbmcvfs.copy(temporary, path)
                xbmcvfs.delete(temporary)
        return True
    except Exception as exc:
        log(f"Could not write {path}: {exc}", xbmc.LOGERROR)
        return False
    finally:
        if handle is not None:
            handle.close()


def sync_state():
    state = read_json(SYNC_STATE_FILE, None)
    if isinstance(state, dict) and state.get("version") is not None:
        return state
    cache = read_json(CACHE_FILE, None)
    return cache if isinstance(cache, dict) else None

startup_sync_done = False


def sync_due():
    frequency = addon.getSetting("sync_frequency") or "manual"

    if frequency == "manual":
        return False
    state = sync_state()
    if not state:
        return False
    if state.get("version") != CACHE_VERSION or state.get("language") != lang():
        log(f"Sync due: cache is v{state.get('version')}/{state.get('language')}, "
            f"this addon wants v{CACHE_VERSION}/{lang()}")
        return True
    if frequency == "startup":
        return not startup_sync_done
    age = int(time.time()) - int(state.get("synced_at") or 0)
    due = age >= (86400 if frequency == "daily" else 7 * 86400)
    if due:
        log(f"Sync due: last one was {age // 3600}h ago, setting is {frequency}")
    return due


def record_playback(asset_id, position, total, finished=False, parent=None):
    points = read_json(PLAYBACK_FILE, {})
    if not isinstance(points, dict):
        points = {}

    points = {k: v for k, v in points.items() if isinstance(v, dict)}
    key = str(asset_id)
    entry = dict(points.get(key) or {})
    try:
        watched = int(entry.get("watched") or 0)
    except (TypeError, ValueError):
        watched = 0
    known = {field: entry[field] for field in ("series", "season") if entry.get(field) is not None}
    for field, value in (parent or {}).items():
        known.setdefault(field, value)
    parent = known

    if finished or (total and position >= total * RESUME_DONE_FRACTION):
        points[key] = dict(parent, watched=watched + 1, finished=int(time.time()))
        outcome = f"watched ({watched + 1}x)"
    elif position < RESUME_MIN_SECONDS:
        if watched:
            points[key] = dict(parent, watched=watched, finished=entry.get("finished"))
        elif parent:
            points[key] = parent
        else:
            points.pop(key, None)
        outcome = "too early, nothing recorded"
    else:
        points[key] = dict(parent, position=round(position, 1), total=round(total, 1),
                           saved=int(time.time()), watched=watched)
        outcome = f"resume at {int(position)}s"

    if write_json(PLAYBACK_FILE, points):
        log(f"Playback recorded for asset={key}: {outcome} (of {int(total)}s)")


class PlaybackTracker(xbmc.Player):
    def __init__(self):
        super().__init__()
        self.asset_id = ""
        self.position = 0.0
        self.total = 0.0
        self.finished = False
        self.parent = {}

        self.lock = threading.Lock()

    def sample(self):
        if not self.asset_id:
            return
        try:
            if self.isPlayingVideo():
                self.position = float(self.getTime())
                self.total = float(self.getTotalTime())
        except Exception as exc:
            log(f"Could not read the playback position: {exc}", xbmc.LOGDEBUG)

    def onAVStarted(self):
        self.position = 0.0
        self.total = 0.0
        self.finished = False

    def onPlayBackStopped(self):
        self.commit()

    def onPlayBackEnded(self):
        self.finished = True
        self.commit()

    def commit(self):
        with self.lock:
            asset_id, position, total, finished, parent = (
                self.asset_id, self.position, self.total, self.finished, self.parent)
            self.asset_id = ""
            self.position = 0.0
            self.total = 0.0
            self.finished = False
            self.parent = {}
        if not asset_id:
            return
        try:
            window = xbmcgui.Window(HOME_WINDOW)
            for name in (PLAYING_PROPERTY, PLAYING_SERIES_PROPERTY, PLAYING_SEASON_PROPERTY):
                window.clearProperty(name)
        except Exception as exc:
            log(f"Could not clear the playing property: {exc}", xbmc.LOGDEBUG)
        record_playback(asset_id, position, total, finished, parent)


def current_asset():
    try:
        return xbmcgui.Window(HOME_WINDOW).getProperty(PLAYING_PROPERTY)
    except Exception:
        return ""


def current_parent():
    parent = {}
    try:
        window = xbmcgui.Window(HOME_WINDOW)
        series = window.getProperty(PLAYING_SERIES_PROPERTY)
        season = window.getProperty(PLAYING_SEASON_PROPERTY)
    except Exception as exc:
        log(f"Could not read the playing title's series: {exc}", xbmc.LOGDEBUG)
        return parent
    if series:
        parent["series"] = series
    if season != "":
        parent["season"] = season
    return parent

monitor = xbmc.Monitor()
player = PlaybackTracker()

log(f"Service started (cache v{CACHE_VERSION}, resume >= {RESUME_MIN_SECONDS}s "
    f"and < {int(RESUME_DONE_FRACTION * 100)}%)")

STARTUP_GRACE = 15
if monitor.waitForAbort(STARTUP_GRACE):
    raise SystemExit

SAMPLE_INTERVAL = 5
SYNC_CHECK_INTERVAL = 300

SYNC_STARTUP_DELAY = 120
next_sync_check = time.time() + SYNC_STARTUP_DELAY

idle_ticks = 0

IDLE_TICKS_BEFORE_GIVING_UP = 24

while not monitor.abortRequested():
    playing = current_asset()
    if playing:
        player.asset_id = playing

        parent = current_parent()
        if parent:
            player.parent = parent
        player.sample()

        try:
            alive = player.isPlaying()
        except Exception:
            alive = True
        if alive:
            idle_ticks = 0
        else:
            idle_ticks += 1
            if idle_ticks >= IDLE_TICKS_BEFORE_GIVING_UP:
                log(f"Nothing has played for asset={playing} in "
                    f"{IDLE_TICKS_BEFORE_GIVING_UP * SAMPLE_INTERVAL}s - releasing it")
                player.commit()
                idle_ticks = 0
    elif player.asset_id:
        player.commit()
        idle_ticks = 0

    now = time.time()
    if now >= next_sync_check:
        next_sync_check = now + SYNC_CHECK_INTERVAL
        if sync_due():
            while player.isPlaying() and not monitor.abortRequested():
                player.sample()
                monitor.waitForAbort(SAMPLE_INTERVAL)
            if monitor.abortRequested():
                break

            startup_sync_done = True
            log("Scheduled sync is due - starting it in the background")
            xbmc.executebuiltin(
                f"RunPlugin(plugin://{ADDON_ID}/?mode=sync&confirm=0&background=1)")
            next_sync_check = time.time() + 3600

    if monitor.waitForAbort(SAMPLE_INTERVAL):
        break

player.commit()
