import re
from bs4 import BeautifulSoup
from kodibgcommon.logging import log_error, log_info, log_last_exception
from .data import categories
from .request_decorator import send_get_request, send_post_request


def get_categories(cat_id):
    items = []
    try:
        for item in categories:
            if item.get("cat_id", 0) == cat_id:
                items.append(item)
    except Exception as er:
        log_error(er)
        log_last_exception()
    return items


def get_products(product_id, page=0):
    """
    Returns all items found on given page
    :param product_id:
    :param page:
    :return:
    """
    items = []
    try:
        response = __get_data_from_api(product_id, page)
        soup = BeautifulSoup(response, 'html5lib')
        divs = soup.find_all('div', class_="item")
        log_info("Extracted %s items with class 'item'" % len(divs))

        i = 0
        for div in divs:
            i += 1
            # log_info(div)
            try:
                title = div.find(class_="title").get_text()
                href = div.find("a")["href"]
                thumb = div.find("img").get("data-src")
                item = {"title": title, "url": href, "thumb": thumb}
                items.append(item)
            except Exception as er:
                log_error(er)
                import traceback
                traceback.print_exc()

    except Exception as er:
        log_error(er)
        log_last_exception()

    return items


def __get_data_from_api(product_id, page):
    payload = get_item(product_id)["payload"]
    payload["page"] = page
    r = send_post_request("https://gong.bg/player/ajax_articles", payload)
    return r.text


def get_item(item_id):
    """
    Get the category item from db by its id
    :param item_id:
    :return:
    """
    try:
        for item in categories:
            if item["id"] == item_id:
                return item
    except Exception as e:
        log_error(e)
        log_last_exception()
    return None


def resolve_mpd_url(url):
    """
    Resolves mpd url from several urls
    :param url: The wrapping page url
    :return: The mpd url
    """

    try:
        response = send_get_request(url)
        log_info("Trying to find video id with regex r'external\\.php\\?vid=(.*?)&'")
        vid = re.compile(r"external\.php\?vid=(.*?)&").findall(response.text)[0]
        url = "https://www.vbox7.com/aj/player/item/options?vid=%s&start=1" % vid
        response = send_get_request(url)
        mpd_url = response.json()["options"]["src"]
        log_info("Resolved mpd url: %s" % mpd_url)

        return mpd_url

    except Exception as er:
        log_error("Error resolving mpd %s" % er)
        log_last_exception()

    return None

