import sys
import xbmcgui
import xbmcplugin
from kodibgcommon.settings import settings
from kodibgcommon.utils import make_url, get_addon_handle
from kodibgcommon.notifications import notify_error, notify_success
from kodibgcommon.logging import log_error, log_info
from .dataaccess import get_categories, get_channels, get_streams, db


def try_db_update():
    """
    Check if db is expired (or missing when first run) and update it
    """
    if not settings.first_run:
        settings.first_run = True
    if not settings.use_local_db and db.is_expired():
        update_db()


def show_categories():
    """
    Creates ListItems with all Channel categories
    """
    categories = get_categories()

    xbmcplugin.addDirectoryItem(
        get_addon_handle(),
        make_url({"id": 0, "action": "show_channels"}),
        xbmcgui.ListItem('Всички'),
        True
    )

    for category in categories:
        xbmcplugin.addDirectoryItem(
            get_addon_handle(),
            make_url({"id": category.id, "action": "show_channels"}),
            xbmcgui.ListItem(category.name),
            True
        )

    if not settings.use_local_db:
        xbmcplugin.addDirectoryItem(
            get_addon_handle(),
            make_url({"action": "update_tvdb"}),
            xbmcgui.ListItem('******** Обнови базата данни ********')
        )

    xbmcplugin.endOfDirectory(int(sys.argv[1]))


def show_channels(category_id):
    """
    Create and show Kodi ListItems for given channel category
    """

    channels = get_channels(category_id)

    for channel in channels:

        if not channel.enabled and not settings.show_only_enabled:
            channel.name = '[COLOR brown]%s[/COLOR]' % channel.name

        li = xbmcgui.ListItem(channel.name)
        li.setInfo(type="Video", infoLabels={"Title": channel.name})
        li.setProperty("isPlayable", str(False))
        li.setArt({"thumb": channel.logo})
        url_items = {"id": channel.id, "action": "show_streams"}
        url = make_url(url_items)

        xbmcplugin.addDirectoryItem(
            get_addon_handle(),
            url,
            li,
            False
        )


def show_streams(channel_id):
    """
    Shows ListItem for streams if there are more than 1. Otherwise just plays the stream.
    """
    streams = get_streams(channel_id)

    selected = 0
    if len(streams) > 1:
        selected = xbmcgui.Dialog().select("Изберете стрийм", [stream.comment for stream in streams])
        if selected == -1:
            return

    url = streams[selected].url

    item = xbmcgui.ListItem(path=url)
    item.setInfo(type="Video", infoLabels={"Title": ''})
    item.setProperty("IsPlayable", str(True))

    xbmcplugin.setResolvedUrl(
        get_addon_handle(),
        succeeded=True,
        listitem=item
    )


def play_channel(channel_id, stream_index=0):
    """
    Extract the available streams for channel and plays the selected one
    """
    try:
        selected_stream = get_streams(id)[stream_index]
        li = xbmcgui.ListItem(selected_stream.name, path=selected_stream.stream_url)
        li.setArt({"thumb": selected_stream.logo})
        li.setInfo(type="Video", infoLabels={"Title": selected_stream.name})
        li.setProperty("IsPlayable", "True")
        xbmcplugin.setResolvedUrl(
            handle=get_addon_handle(),
            succeeded=True,
            listitem=li
        )
    except Exception as er:
        log_error(er)
        notify_error(er)


def update_db():
    """
    Manually updates the channels DB
    """

    progress_bar = xbmcgui.DialogProgressBG()
    progress_bar.create(heading="Сваляне на файла с базата данни")

    msg = "Базата данни НЕ бе обновена!"

    try:
        log_info('Manual DB update')
        progress_bar.update(1, "Downloading DB")
        res = db.update()
        if res:
            msg = "Базата данни бе обновена успешно!"
        if settings.use_local_db:
            msg += " Използвате локална база данни!"

    except Exception as ex:
        log_error(ex)
        notify_error(ex, True)

    notify_success(msg)

    if progress_bar:
        progress_bar.close()
