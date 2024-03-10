import xbmcgui
import xbmcplugin
from kodibgcommon.logging import log_info, log_error
from kodibgcommon.notifications import notify_error
from kodibgcommon.utils import get_addon_handle, make_url, add_listitem_folder
from .dataaccess import get_categories, get_products, resolve_mpd_url


def show_categories(params):
    """
    Builds the list items for the available categories
    :param params:
    """

    cat_id = int(params.get("id", 0))

    for category in get_categories(cat_id):
        action = "show_categories" if cat_id == 0 else "show_products"
        url = make_url({"id": category.get("id"), "action": action})

        add_listitem_folder(category["name"], url)


def show_products(params):
    """
    Builds the list items for given product category
    :param params:
    :return:
    """
    product_id = int(params.get("id"))
    page = int(params.get("page", 1))

    products = get_products(product_id, page)

    for product in products:

        try:
            li = xbmcgui.ListItem(product["title"])
            li.setProperty("IsPlayable", 'True')
            li.setArt({"thumb": product.get("thumb")})

            xbmcplugin.addDirectoryItem(
                get_addon_handle(),
                make_url({"url": product["url"], "action": "play_stream"}),
                li,
                False
            )

        except Exception as er:
            log_error("Error adding list item for product '%s': %s" % (product.get("title"), er))

    url = make_url({"id": product_id, "action": "show_products", "page": page + 1})
    add_listitem_folder("Следваща страница", url)


def play_stream(params):
    """
    Extract the available mpd file for item and play the selected one
    """
    try:
        url = params.get("url")
        mpd_url = resolve_mpd_url(url)
        if not mpd_url:
            log_error("Unable to extract mdp_url")
            notify_error("Неуспешно намерен УРЛ на видео поток")
            return

        list_item = xbmcgui.ListItem(path=mpd_url)
        list_item.setMimeType('application/xml+dash')
        list_item.setContentLookup(False)

        list_item.setProperty('inputstream', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')  # Deprecated on Kodi 21

        xbmcplugin.setResolvedUrl(
            get_addon_handle(),
            True,
            listitem=list_item
        )

    except Exception as er:
        log_info("Error setting the resolved URL %s" % er)
        notify_error("Грешка при извличането на видео поток: %s" % er)
