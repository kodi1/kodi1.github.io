# file: page_scraper.py
import re
import urllib
import ssl
from bs4 import BeautifulSoup
from urllib import request, parse


class PageScraper:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    next_page_title = 'Следваща страница'

    sections = [
        {'title': 'Предавания', "path": "predavaniya", "action": "show_products", "testable": True},
        {'title': 'Сериали', "path": "seriali", "action": "show_products", "testable": True},
        {'title': 'Емисии', "path": "novini", "action": "show_products", "testable": True},
        {'title': 'Търсене', "path": "search", "action": "search", "testable": False},
    ]

    def __init__(self, log_delegate, host: str):
        """
        Initialize the PageScraper.

        Args:
            log (callable): A logging function or object used for logging messages.
                                     Expected to have a method like log_delegate(message) or
                                     log_delegate.info(message), depending on usage.
            host (str): The base URL or hostname to scrape pages from.
        """
        self.log = log_delegate
        self.host = host

        if callable(log_delegate):
            self._log = log_delegate
        elif hasattr(log_delegate, "info"):
            self._log = log_delegate.info
        else:
            raise TypeError("log_delegate must be callable or have an 'info' method")

        self._log(f"PageScraper initialized for host: {host}")

    def get_items(self, path):
        '''
      Get all items from the 'predavaniya' and 'seriali' pages
      Products have no titles, only icons
      '''

        results = []
        url = urllib.parse.urljoin(self.host, path)
        self.log("GET " + url, 2)
        ssl._create_default_https_context = ssl._create_unverified_context
        req = urllib.request.Request(url)
        req.add_header('User-agent', self.user_agent)
        text = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(text, 'html5lib')
        items = soup.find_all("article", class_='card')

        for item in items:
            logoUrl = item.find("img")["src"]
            linkEl = item.find("a")
            if linkEl:
                href = urllib.parse.urljoin(self.host, linkEl["href"])
                title = linkEl.get_text().rstrip()
            else:
                linkEl = item.find("button")

                title = item.find(class_='card__label').get_text().rstrip()
                title = "%s: %s" % (title, linkEl.get("data-title"))
                href = linkEl.get("data-url")

            item = {"title": title, "path": href, "logo": logoUrl}
            results.append(item)

        return results

    def get_stream(self, url):
        url = urllib.parse.urljoin(self.host, url)
        self.log("Opening show URL GET " + url, 1)
        ssl._create_default_https_context = ssl._create_unverified_context
        req = urllib.request.Request(url)
        req.add_header("Referer", self.host)
        req.add_header("User-agent", self.user_agent)
        text = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(text, 'html5lib')
        item = {"url": None, "logo": None}
        # log(text, 1)
        title = soup.title.get_text()
        # looking for something like this var videoUrl = '/lbin/v3/btvplus/product_player.php?product_id=64874&product_parent_id=54557&type_id=100';
        m = re.compile("var videoUrl = '(.*?)';").findall(text)
        if len(m) > 0:
            player_url = url = urllib.parse.urljoin(self.host, m[0])
            self.log("Opening player url " + player_url, 1)
            req = urllib.request.Request(player_url)
            req.add_header("Referer", url)
            req.add_header("User-agent", "Chrome")
            text = urllib.request.urlopen(req).read().decode('utf-8')

            m = re.compile("src\s*:\s*\'(http.+?m3u8)").findall(text)
            if len(m) > 0:
                item["url"] = m[0].replace("\/", "/")
                self.log("resolved stream: %s" % item["url"], 0)
            else:
                self.log("No m3u stream found in response: ", 4)
                self.log(text, 4)
            # m = re.compile('poster[:\s\'"]+(http.*jpg)').findall(text)
            # if len(m) > 0:
            #   item["logo"] = m[0]
            #   if not item["logo"].startswith("http"):
            #     item["logo"] = 'https:'+ item["logo"]
        else:
            self.log("No streams found!", 4)
            # Notification("Грешка", "Видеото не е налично! Вероятно е премахнато от сайта!")
        return item

