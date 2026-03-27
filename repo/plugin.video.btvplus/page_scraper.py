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

    def get_items(self, path, send_post=False):
        '''
      Get all items from the 'predavaniya' and 'seriali' pages
      Products have no titles, only icons
      '''
        results = []
        ssl._create_default_https_context = ssl._create_unverified_context

        if send_post:

            self.log("POST " + path, 2)
            url = "https://btvplus.bg/lbin/v3/btvplus/changeTab.php"
            payload = {"tab": "latest", "apiurl": "/%s" % path.replace(self.host, ""), "page": 1}
            self.log(payload)
            data = urllib.parse.urlencode(payload).encode('utf-8')

            # Create the request with method POST
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('User-agent', self.user_agent)
            req.add_header('Content-Type', 'application/json')
            req.add_header('Referer', self.host)
            req.add_header('Cookie', "utag=65adaf59031930bf2f70178ea43c133368a4998a98289; _fbp=fb.1.1755617748338.351208254490837442; _gid=GA1.2.621594222.1762702170; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CQWZXEAQWZXEAEsACBBGB4FoAP_gAEPgABpYKUJB7C7lbSFCyL5zaLsAcAhHx8AAYoQAAASBgmABQAKQIAwCgmA4FASABAACABAAIGRBIQIECAAAAUAAAAAAAAAAAAAQAAAIIAAAgAEBAiBICAACAIBAEQAIAABAEAAAmAgAAIIASAAAgAAAgAAAAAAAABAAAACAAAgAAAAAAAAAAAQAAQJAAAAAAAAIAABAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAQUoSD2F3K2kKFkXCmwXYAYBCvj4AAxQgAAAkDBMACgAUgQBgFJMBgCIEAAAAAACAAQMiCQAAQEBAAAIACAAAAAAAAAAAgAAAQQAABAAICBECAAAAEAQCAIgAQAACAIAABEhAAAQQAkAAAAAABQAAAAAAAACAAAAAAIBAAAAAAAAAAAAgAAASAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAA.digACAAAAAA%22%2C%222~70.89.93.108.122.149.184.196.236.259.311.313.314.323.358.415.442.486.494.495.540.574.723.827.864.981.1029.1047.1048.1051.1095.1097.1126.1205.1276.1301.1365.1415.1449.1514.1570.1577.1598.1651.1716.1735.1753.1765.1870.1878.1889.1958.2072.2253.2299.2373.2415.2506.2526.2531.2568.2571.2575.2624.2677.2778~dv.%22%2C%22B2629FED-902B-42E7-8004-0B2DB7835327%22%5D%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22335200cd-b6fb-4fd1-860c-7bc15db46a60%5C%22%2C%5B1762702170%2C539000000%5D%5D%22%5D%5D%5D; pbjs-unifiedid=%7B%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222025-11-09T15%3A30%3A58%22%7D; pbjs-unifiedid_cst=kCwNLLEsKw%3D%3D; panoramaId_expiry=1763307058552; _cc_id=bf007c3774e91dc764005b40af37f69e; panoramaId=3ce27f53cf6a24d85c85242b4832185ca02cad459344cf2727d3c72e84b283ec; PHPSESSID=nvhuaia1hj3k5mor848p2fcqnh; cf_clearance=tT6kPuEELXTIaRUvhGJ.wmfb6j1vMk3R82mvJDObQCE-1762702297-1.2.1.1-5_tCJPH.5ABl7efI6_8aZD2ekjRq9diZ0va1lFU7kwdKwnsBMkkr3DBQXWHecWDBTqPFDUvuJ0mw9qO8EkhGAIbHC5ROqU4wAmE.dCz9TbzhmFoiyQMkiEfVZJYrxiwhO6qBlsWQ8C5I.ntCaepyIMhyXdUz2vVRr9XbBsdObTbyzaZEAF7fetaxG_vSjzsGIfFV4C6uz_hnfudDdSnV35urTXpZWZHg3m3oiB4BLvY; _cfuvid=QCLK6DSnJARqI26AmLDE8EkEqyNyXbY3V6EOZW6Y7s0-1762702864607-0.0.1.1-604800000; _ga=GA1.1.336724498.1755617747; _ga_EBNQBL9MJY=GS2.2.s1762702171$o3$g1$t1762702914$j59$l0$h0; _ga_1B9Y263MTC=GS2.1.s1762702171$o4$g1$t1762702915$j60$l0$h0; cto_bidid=LEhfel95M3dFZnJWVDFpWGlna1JRMGh6TDYzRVlNJTJGbjhHVko2TW5KSFF6N3psMHRpQ0tjUnBuUU9ETGMweEptSVd5cU04cTlEaGZiakslMkJBYVlCcnJ3Q2hKMGprQlFpSWNFU0V4SjNoZ1VmenlQYlElM0Q; cto_bundle=X4BDV19nNlIyWU5TakNja1lNZlVyZEtiNTdLbDExcGRUbDNlUFBqJTJGMEhLdVZEQTFSM1pyUnNBbEZkcklwbWdWRlA4RkpDelZQemtVdmN1OEdubkg1bzVGWVhKOGZXWnNObldQa00wYWdSZjdqb09JOSUyRkc3MSUyQkRoNzMlMkZZZ2NNYVNBQlFtMEZWSmRhWVJuMlo3TDJFbG5wQ0RWZ1l5QUZMVGV3bkg5V2J1JTJCVjdzcDBKQld2MjQ5SUt4RVI1dGFYWm5EeVRn; FCNEC=%5B%5B%22AKsRol916cj2t6JGvXejnFOdh9pEiSRs0UmP794ywisQ86oCmVIdd4uFsU3FDiQyGIdH2w8m1g-5mrfi9BLn-BaJy47nZZ0tYzPi3bNgYYhuYZcDFBWpMdOk_5C16DETSOGHppQ9NzdvB25yfW45YdPoI8SKk8nfWg%3D%3D%22%5D%5D; _ga_ZDBMS8FR9P=GS2.1.s1762702170$o4$g1$t1762703028$j55$l0$h0; _ga_7BTJ02DQ26=GS2.1.s1762702170$o4$g1$t1762703028$j55$l0$h0; __gads=ID=cb7d81d0df43f444:T=1755617750:RT=1762703516:S=ALNI_MbwNFWUaj3giX9po-99bHGnpEW3Fg; __gpi=UID=0000112eb15475a8:T=1755617750:RT=1762703516:S=ALNI_MY1dIpgcLwZ-_88O84MLTv09bOL6Q; __eoi=ID=ac6ff7e83a2c8ab6:T=1755617750:RT=1762703516:S=AA-AfjZkRzvpqPi0J4qFOCNs2lAJ")

            # Perform the request
            text = urllib.request.urlopen(req).read().decode('utf-8')
            # soup = BeautifulSoup(text, 'html5lib')

            self.log("response: %s" % text, 2)
        else:
            url = urllib.parse.urljoin(self.host, path)
            self.log("GET " + url, 2)

            req = urllib.request.Request(url)
            req.add_header('User-agent', self.user_agent)
            text = urllib.request.urlopen(req).read().decode('utf-8')
            soup = BeautifulSoup(text, 'html5lib')
            items = soup.find_all("article", class_='card')

            tabs = soup.find_all(class_="tablinks")
            self.log("Found %s" % len(tabs))
            for t in tabs:
                button_text = t.find(class_="button__text")
                if button_text:
                    results.append({"title": button_text.get_text().rstrip(), "path": urllib.parse.urljoin(self.host, t.get("data-apiurl")), "logo": "", "playable": False, "post": True})

            for item in items:
                logoUrl = item.find("img")["src"]
                linkEl = item.find("a")
                if linkEl:
                    href = urllib.parse.urljoin(self.host, linkEl["href"])
                    title = linkEl.get_text().lstrip().rstrip()
                else:
                    linkEl = item.find("button")

                    title1 = ""
                    card_label = item.find(class_='card__label')
                    if card_label:
                        title1 = "%s: " % card_label.get_text().lstrip().rstrip()

                    title = "%s%s" % (title1, linkEl.get("data-title"))
                    href = linkEl.get("data-url")

                subtitles = item.find_all(class_='card__tag')
                if len(subtitles) > 0:
                    for s in subtitles:
                        txt = s.find('span')
                        if txt:
                            title += " %s" % txt.get_text().lstrip().rstrip()

                plot = ""
                parent_div = item.parent
                if parent_div and parent_div.has_attr("data-description"):
                    plot = parent_div["data-description"]

                item = {"title": title, "path": href, "logo": logoUrl, "playable": True, "plot": plot}
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

