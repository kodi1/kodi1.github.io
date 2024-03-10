import requests

from kodibgcommon.settings import settings
from kodibgcommon.logging import log_info

headers = {"User-agent": "Mozilla", "Referer": "https://gong.bg"}


def send_get_request(url):

    __log_debug("GET %s" % url)
    __log_debug(headers)
    r = requests.get(url, headers=headers)
    __log_debug("Received status code: %s" % r.status_code)
    __log_debug(r.text)

    return r


def send_post_request(url, data=None):

    __log_debug("POST %s" % url)
    __log_debug(headers)
    r = requests.post(url, headers=headers, data=data)
    __log_debug("Received status code: %s" % r.status_code)
    __log_debug(r.text)

    return r


def __log_debug(msg):
    if settings.debug:
        log_info(msg)
