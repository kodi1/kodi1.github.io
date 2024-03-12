import os
import sqlite3
from .playlist import Category, Channel, Stream
from .assets import DbAsset
from kodibgcommon.settings import settings
from kodibgcommon.utils import get_profile_dir
from kodibgcommon.notifications import notify_error, notify_success
from kodibgcommon.logging import log_info, log_error, log

db_file_path = os.path.join(get_profile_dir(), 'tvs.sqlite3')
if settings.use_local_db and settings.db_file_path != '' and os.path.isfile(settings.db_file_path):
    db_file_path = settings.db_file_path

db = DbAsset(
    log_delegate=log,
    url=settings.url_to_db,
    file_path=db_file_path
)


def get_categories():
    """
    Returns all categories from DB
    """
    categories = []

    try:
        conn = sqlite3.connect(db_file_path)
        query = "SELECT * FROM freetvandradio_category"
        conn.row_factory = lambda cursor, row: Category(row)
        c = conn.cursor()
        categories = c.execute(query).fetchall()

    except Exception as er:
        log_error(er)
        notify_error(er)

    return categories


def get_channels(category_id):
    """
    Returns all channels from DB for given category
    """

    channels = []

    try:
        log_info("Getting channel for category id: %s" % category_id)

        conn = sqlite3.connect(db_file_path)
        query = '''SELECT channel_id FROM freetvandradio_channel_category AS cc '''
        # if we are showing all channels, that is category_id is 0 and show radios is disabled
        if int(category_id) > 0:
            query += "WHERE cc.category_id = %s;" % category_id

        conn.row_factory = lambda cursor, row: row[0]
        c = conn.cursor()
        ids = c.execute(query).fetchall()
        ids = ','.join(str(id) for id in ids)

        query_get_only_enabled = '''AND ch.enabled = 1''' if settings.show_only_enabled else ''
        query = '''SELECT ch.id, ch.name, ch.logo, ch.ordering, ch.enabled FROM freetvandradio_channel AS ch WHERE ch.id 
        IN (%s) %s GROUP BY ch.id ORDER BY ch.ordering''' % (ids, query_get_only_enabled)

        conn.row_factory = lambda cursor, row: Channel(row)
        c = conn.cursor()
        channels = c.execute(query).fetchall()

        log_info("Extracted %s channels" % len(channels))

    except Exception as er:
        log_error(er)
    return channels


def get_streams(channel_id):
    """
    Gets all available streams for the given channel from DB
    """

    streams = []

    try:
        log_info("Using db: %s " % db_file_path)
        conn = sqlite3.connect(db_file_path)
        query = ("SELECT s.id, s.channel_id, s.stream_url, s.page_url, s.player_url, s.enabled, s.comment, u.string AS "
                 "user_agent, s.regex, s.stream_referer "
                 "FROM freetvandradio_stream AS s "
                 "JOIN freetvandradio_user_agent as u ON s.user_agent_id==u.id "
                 "WHERE channel_id=%s" % channel_id)

        if settings.show_only_enabled:
            query += " AND s.enabled=1"

        log_info("Query: %s " % query)
        conn.row_factory = lambda cursor, row: Stream(row)
        c = conn.cursor()

        streams = c.execute(query).fetchall()

    except Exception as er:
        log_error(er)

    return streams
