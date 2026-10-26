from __future__ import annotations

import base64
import json
import os
import sys
import time
import threading
import traceback
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, parse_qsl, urlparse, quote
import ssl
from urllib.request import Request, urlopen, build_opener, install_opener, HTTPSHandler

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs


def _https_context() -> ssl.SSLContext:
    # On Windows, Python loads the Windows certificate store first. A single certificate
    # there that Kodi's OpenSSL cannot parse makes every HTTPS call fail with
    # "cadata does not contain a certificate". pvr.eon is unaffected because Kodi's curl
    # uses its own CA bundle, so fall back to that same bundle. Verification stays on.
    try:
        return ssl.create_default_context()
    except ssl.SSLError as exc:
        xbmc.log(f"[plugin.video.eonvod] System certificate store unusable ({exc}); "
                 f"using Kodi's CA bundle instead", xbmc.LOGWARNING)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    bundle = xbmcvfs.translatePath("special://xbmc/system/certs/cacert.pem")
    if os.path.isfile(bundle):
        context.load_verify_locations(cafile=bundle)
    else:
        context.set_default_verify_paths()
    return context


install_opener(build_opener(HTTPSHandler(context=_https_context())))

ADDON = xbmcaddon.Addon()
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

ADDON_ID = ADDON.getAddonInfo("id") or "plugin.video.eonvod"

ADDON_NAME = ADDON.getAddonInfo("name") or "EON On Demand"

ADDON_PATH = ADDON.getAddonInfo("path")

PVR_ADDON_ID = "pvr.eon"

HOME_WINDOW = 10000

PLAYING_PROPERTY = "eonvod.playing"
PLAYING_SERIES_PROPERTY = "eonvod.playing.series"
PLAYING_SEASON_PROPERTY = "eonvod.playing.season"

API = "https://api-web.ug-be.cdn.united.cloud/"
IMAGES = "https://images-web.ug-be.cdn.united.cloud"
BROKER_URL = "https://broker.global.united.cloud/"
API_SELECTOR = "be"

#   index   up to 21.8.5        21.8.5.1 and later
#   0       SBB                 SBB
#   1       Telemach            Telemach
#   2       NetTV Plus          Telemach HR
#   3       Vivacom             Telemach SI
#   4       EON Hrvatska        Vivacom
#   5       Nova                Nova

PROVIDER_BRAND_IDENTIFIERS = {
    "0": "sbb-qa",
    "1": "telemach",
    "2": "telemach-hr",
    "3": "telemach-si",
    "4": "vivacom",
    "5": "nova",
}

LEGACY_PROVIDER_BRAND_IDENTIFIERS = {
    "0": "sbb-qa",
    "1": "telemach",
    "3": "vivacom",
    "5": "nova",
}

PROVIDER_LIST_CHANGED_IN = (21, 8, 5, 1)

WEB_CLIENT_ID = "b8d9ade4-1093-46a7-a4f7-0e47be463c10"
WEB_CLIENT_SECRET = "1w4dmww87x1e9l89essqvc81pidrqsa0li1rva23"

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"


def user_agent() -> str:
    try:
        if as_bool(ADDON.getSetting("usecustomuseragent"), False):
            custom = (ADDON.getSetting("customuseragent") or "").strip()
            if custom:
                return custom
    except Exception:
        pass
    return DEFAULT_USER_AGENT

PLAYER_VOD = "fm3u8vcbcs"
CONN_TYPE = "BROWSER"
STREAM_LANG = "eng"
STREAM_NOFPS_INFO = "false"

PAGE_SIZE = 50

MIN_SEARCH_LENGTH = 3

CACHE_VERSION = 1

THEMED_PAGES = {
    "theme_short30": ("10036", "Under 30 min"),
    "theme_short60": ("10037", "Under 60 min"),
    "theme_laughs": ("10038", "Just for laughs"),
    "theme_love": ("10039", "Love Stories"),
    "theme_fantasy": ("10040", "Fantasy worlds"),
    "theme_nature": ("10041", "Nature and knowledge"),
    "theme_thrills": ("10042", "Chills and Thrills"),
    "theme_people": ("10043", "People and places"),
}

SYNC_PAGES = {
    "home": "10001",
    "movies": "10003",
    "series": "10004",
    "kids": "10005",
    "documentaries": "10007",
    "tvshows": "10006"
}
SYNC_PAGES.update({key: page for key, (page, _title) in THEMED_PAGES.items()})

PORTAL_PAGES = {
    "vivacom": {"home": "10001", "movies": "10003", "series": "10004", "kids": "10005", "documentaries": "10006"},
    "forthnet": {"home": "10001", "movies": "10003", "series": "10004", "kids": "10005", "documentaries": "10006"},
}

def portal_pages(cdn_identifier: str = "") -> dict[str, str]:
    return dict(PORTAL_PAGES.get(str(cdn_identifier or "").casefold()) or SYNC_PAGES)

ADDON_DATA = xbmcvfs.translatePath(ADDON.getAddonInfo("profile") or
                                   f"special://profile/addon_data/{ADDON_ID}/")
if not ADDON_DATA.endswith("/"):
    ADDON_DATA += "/"

CACHE_FILE = ADDON_DATA + "vod_cache.json"

LEGACY_CACHE_FILE = xbmcvfs.translatePath(
    f"special://profile/addon_data/{PVR_ADDON_ID}/vod_cache.json")

FAVORITES_FILE = ADDON_DATA + "favorites.json"

SEARCHES_FILE = ADDON_DATA + "searches.json"
MAX_SEARCH_HISTORY = 10

SESSION_FILE = ADDON_DATA + "session.json"

PLAYBACK_FILE = ADDON_DATA + "playback.json"

SYNC_STATE_FILE = ADDON_DATA + "sync_state.json"

RESUME_MIN_SECONDS = 60
RESUME_DONE_FRACTION = 0.90
SESSION_MAX_AGE = 3600

SECTIONS = {
    "movies": {"title": "Movies", "page": "10003", "category": "201"},
    "series": {"title": "Series", "page": "10004", "category": "202"},
    "kids": {"title": "Kids", "page": "10005", "category": "203"},
    "documentaries": {"title": "Documentaries", "page": "10007", "category": "207", "genre": "9"},
    "tvshows": {"title": "TV Shows", "page": "10006", "category": "209"},
    "home": {"title": "Home", "page": "10001"},
}

SECTION_BY_CATEGORY = {config["category"]: key for key, config in SECTIONS.items()
                       if config.get("category")}

SECTIONS.update(
    {key: {"title": title, "page": page, "parent": "home"} for key, (page, title) in THEMED_PAGES.items()}
)

sys.path.insert(0, xbmcvfs.translatePath(ADDON_PATH + "/resources/lib"))
import pyaes


def notify(message: str, seconds: int = 5000) -> None:
    xbmcgui.Dialog().notification(ADDON_NAME, message, addon_icon(), seconds)


def log(message: str, level: int = xbmc.LOGINFO) -> None:
    for line in str(message).splitlines() or [""]:
        xbmc.log(f"[{ADDON_ID}] {line}", level)


def plugin_url(**params: Any) -> str:
    return BASE_URL + "?" + urlencode({k: v for k, v in params.items() if v is not None})


def encode_data(value: dict[str, Any]) -> str:
    payload = json.dumps(value, separators=(",", ":")).encode("utf-8")
    return b64url_encode(payload)


def decode_data(value: str) -> dict[str, Any]:
    return json.loads(b64url_decode(value).decode("utf-8"))


def image_url(path: str | None) -> str:
    if not path:
        return ""
    if path.startswith("http"):
        return path
    return IMAGES + path


def as_bool(value: str, default: bool = False) -> bool:
    if value == "":
        return default
    return value.lower() in ("true", "1", "yes")


def page_size() -> int:
    try:
        return max(5, int(ADDON.getSetting("page_size") or PAGE_SIZE))
    except ValueError:
        return PAGE_SIZE


METADATA_LANGUAGES = ("eng", "srp", "bos", "hrv", "slv", "mne", "mac", "bul", "gre")

def metadata_language() -> str:
    lang = ADDON.getSetting("metadata_language") or "eng"
    return lang if lang in METADATA_LANGUAGES else "eng"


TEXTS: dict[str, dict[str, str]] = {

    "syncing": {
        "eng": "Syncing with EON TV API",
        "srp": "Sinhronizacija sa EON TV API",
        "bos": "Sinhronizacija sa EON TV API",
        "hrv": "Sinkronizacija s EON TV API",
        "slv": "Sinhronizacija z EON TV API",
        "mne": "Sinhronizacija sa EON TV API",
        "mac": "Синхронизација со EON TV API",
        "bul": "Синхронизиране с EON TV API",
        "gre": "Συγχρονισμός με το EON TV API"
    },
    "loading_page": {
        "eng": "Loading page",
        "srp": "Učitavanje stranice",
        "bos": "Učitavanje stranice",
        "hrv": "Učitavanje stranice",
        "slv": "Nalaganje strani",
        "mne": "Učitavanje stranice",
        "mac": "Вчитување на страницата",
        "bul": "Зареждане на страница",
        "gre": "Φόρτωση σελίδας"
    },
    "loading": {
        "eng": "Loading",
        "srp": "Učitavanje",
        "bos": "Učitavanje",
        "hrv": "Učitavanje",
        "slv": "Nalaganje",
        "mne": "Učitavanje",
        "mac": "Вчитување",
        "bul": "Зареждане",
        "gre": "Φόρτωση"
    },
    "checking": {
        "eng": "Checking item",
        "srp": "Provera stavke",
        "bos": "Provjera stavke",
        "hrv": "Provjera stavke",
        "slv": "Preverjanje elementa",
        "mne": "Provjera stavke",
        "mac": "Проверка на ставката",
        "bul": "Проверка на елемент",
        "gre": "Έλεγχος στοιχείου"
    },
    "saving": {
        "eng": "Saving cache",
        "srp": "Čuvanje keša",
        "bos": "Čuvanje keša",
        "hrv": "Spremanje predmemorije",
        "slv": "Shranjevanje predpomnilnika",
        "mne": "Čuvanje keša",
        "mac": "Зачувување на кешот",
        "bul": "Запис на кеш",
        "gre": "Αποθήκευση προσωρινής μνήμης"
    },
    "synced": {
        "eng": "Synced",
        "srp": "Sinhronizovano",
        "bos": "Sinhronizovano",
        "hrv": "Sinkronizirano",
        "slv": "Sinhronizirano",
        "mne": "Sinhronizovano",
        "mac": "Синхронизирано",
        "bul": "Синхронизирани",
        "gre": "Συγχρονίστηκε"
    },
    "sync_empty": {
        "eng": "Sync returned no titles. The previous catalogue has been kept. Check the log.",
        "srp": "Sinhronizacija nije vratila nijedan naslov. Prethodni katalog je sačuvan. Proverite log.",
        "bos": "Sinhronizacija nije vratila nijedan naslov. Prethodni katalog je sačuvan. Provjerite log.",
        "hrv": "Sinkronizacija nije vratila nijedan naslov. Prethodni katalog je sačuvan. Provjerite zapisnik.",
        "slv": "Sinhronizacija ni vrnila naslovov. Prejšnji katalog je ohranjen. Preverite log.",
        "mne": "Sinhronizacija nije vratila nijedan naslov. Prethodni katalog je sačuvan. Provjerite log.",
        "mac": "Синхронизацијата не врати ниту еден наслов. Претходниот каталог е зачуван. Проверете го логот.",
        "bul": "Синхронизацията не върна заглавия. Предишният каталог е запазен. Проверете лога.",
        "gre": "Ο συγχρονισμός δεν επέστρεψε τίτλους. Ο προηγούμενος κατάλογος διατηρήθηκε. Ελέγξτε το αρχείο καταγραφής."
    },
    "items": {
        "eng": "VOD items",
        "srp": "VOD stavki",
        "bos": "VOD stavki",
        "hrv": "VOD stavki",
        "slv": "VOD elementov",
        "mne": "VOD stavki",
        "mac": "VOD ставки",
        "bul": "VOD елемента",
        "gre": "Στοιχεία VOD"
    },
    "movies": {
        "eng": "Movies",
        "srp": "Filmovi",
        "bos": "Filmovi",
        "hrv": "Filmovi",
        "slv": "Filmi",
        "mne": "Filmovi",
        "mac": "Филмови",
        "bul": "Филми",
        "gre": "Ταινίες"
    },
    "series": {
        "eng": "Series",
        "srp": "Serije",
        "bos": "Serije",
        "hrv": "Serije",
        "slv": "Serije",
        "mne": "Serije",
        "mac": "Серии",
        "bul": "Сериали",
        "gre": "Σειρές"
    },
    "kids": {
        "eng": "Kids",
        "srp": "Dečiji",
        "bos": "Dječiji",
        "hrv": "Dječji",
        "slv": "Otroški",
        "mne": "Dječiji",
        "mac": "Детски",
        "bul": "Детски",
        "gre": "Παιδικά"
    },
    "tvshows": {
        "eng": "TV Shows",
        "srp": "TV emisije",
        "bos": "TV emisije",
        "hrv": "TV emisije",
        "slv": "TV oddaje",
        "mne": "TV emisije",
        "mac": "ТВ емисии",
        "bul": "ТВ предавания",
        "gre": "Τηλεοπτικές εκπομπές"
    },
    "home": {
        "eng": "Home",
        "srp": "Naslovna",
        "bos": "Naslovna",
        "hrv": "Naslovnica",
        "slv": "Začetna",
        "mne": "Naslovna",
        "mac": "Почетна",
        "bul": "Начало",
        "gre": "Αρχική"
    },
    "documentaries": {
        "eng": "Documentaries",
        "srp": "Dokumentarci",
        "bos": "Dokumentarci",
        "hrv": "Dokumentarci",
        "slv": "Dokumentarci",
        "mne": "Dokumentarci",
        "mac": "Документарци",
        "bul": "Документални",
        "gre": "Ντοκιμαντέρ"
    },
    "tv_networks": {
        "eng": "TV Networks",
        "srp": "TV mreže",
        "bos": "TV mreže",
        "hrv": "TV mreže",
        "slv": "TV mreže",
        "mne": "TV mreže",
        "mac": "ТВ мрежи",
        "bul": "ТВ мрежи",
        "gre": "Τηλεοπτικά δίκτυα"
    },
    "next_page": {
        "eng": "Next page",
        "srp": "Sledeća strana",
        "bos": "Sljedeća stranica",
        "hrv": "Sljedeća stranica",
        "slv": "Naslednja stran",
        "mne": "Sljedeća stranica",
        "mac": "Следна страница",
        "bul": "Следваща страница",
        "gre": "Επόμενη σελίδα"
    },
    "tools": {
        "eng": "Tools",
        "srp": "Alati",
        "bos": "Alati",
        "hrv": "Alati",
        "slv": "Orodja",
        "mne": "Alati",
        "mac": "Алатки",
        "bul": "Инструменти",
        "gre": "Εργαλεία"
    },
    "categories": {
        "eng": "Categories",
        "srp": "Kategorije",
        "bos": "Kategorije",
        "hrv": "Kategorije",
        "slv": "Kategorije",
        "mne": "Kategorije",
        "mac": "Категории",
        "bul": "Категории",
        "gre": "Κατηγορίες"
    },
    "favorites": {
        "eng": "Favourites",
        "srp": "Favoriti",
        "bos": "Favoriti",
        "hrv": "Favoriti",
        "slv": "Priljubljeni",
        "mne": "Favoriti",
        "mac": "Омилени",
        "bul": "Любими",
        "gre": "Αγαπημένα"
    },
    "fav_add": {
        "eng": "Add to EON favourites",
        "srp": "Dodaj u EON favorite",
        "bos": "Dodaj u EON favorite",
        "hrv": "Dodaj u EON favorite",
        "slv": "Dodaj med EON priljubljene",
        "mne": "Dodaj u EON favorite",
        "mac": "Додај во EON омилени",
        "bul": "Добави в EON любими",
        "gre": "Προσθήκη στα αγαπημένα EON"
    },
    "fav_remove": {
        "eng": "Remove from EON favourites",
        "srp": "Ukloni iz EON favorita",
        "bos": "Ukloni iz EON favorita",
        "hrv": "Ukloni iz EON favorita",
        "slv": "Odstrani iz EON priljubljenih",
        "mne": "Ukloni iz EON favorita",
        "mac": "Отстрани од EON омилени",
        "bul": "Премахни от EON любими",
        "gre": "Αφαίρεση από τα αγαπημένα EON"
    },
    "fav_clear": {
        "eng": "Remove all from EON favourites",
        "srp": "Ukloni sve iz EON favorita",
        "bos": "Ukloni sve iz EON favorita",
        "hrv": "Ukloni sve iz EON favorita",
        "slv": "Odstrani vse iz EON priljubljenih",
        "mne": "Ukloni sve iz EON favorita",
        "mac": "Отстрани ги сите од EON омилени",
        "bul": "Изчисти EON любими",
        "gre": "Αφαίρεση όλων από τα αγαπημένα EON"
    },
    "fav_clear_ask": {
        "eng": "Remove all favourites?",
        "srp": "Ukloniti sve iz favorita?",
        "bos": "Ukloniti sve iz favorita?",
        "hrv": "Ukloniti sve iz favorita?",
        "slv": "Naj odstranim vse priljubljene?",
        "mne": "Ukloniti sve iz favorita?",
        "mac": "Да ги отстранам сите омилени?",
        "bul": "Да изчистя ли всички любими?",
        "gre": "Αφαίρεση όλων των αγαπημένων;"
    },
    "fav_added": {
        "eng": "Added to favourites",
        "srp": "Dodato u favorite",
        "bos": "Dodato u favorite",
        "hrv": "Dodano u favorite",
        "slv": "Dodano med priljubljene",
        "mne": "Dodato u favorite",
        "mac": "Додадено во омилени",
        "bul": "Добавено в любими",
        "gre": "Προστέθηκε στα αγαπημένα"
    },
    "fav_removed": {
        "eng": "Removed from favourites",
        "srp": "Uklonjeno iz favorita",
        "bos": "Uklonjeno iz favorita",
        "hrv": "Uklonjeno iz favorita",
        "slv": "Odstranjeno iz priljubljenih",
        "mne": "Uklonjeno iz favorita",
        "mac": "Отстрането од омилени",
        "bul": "Премахнато от любими",
        "gre": "Αφαιρέθηκε από τα αγαπημένα"
    },
    "fav_cleared": {
        "eng": "Favourites cleared",
        "srp": "Favoriti su ispražnjeni",
        "bos": "Favoriti su ispražnjeni",
        "hrv": "Favoriti su ispražnjeni",
        "slv": "Priljubljeni so izbrisani",
        "mne": "Favoriti su ispražnjeni",
        "mac": "Омилените се испразнети",
        "bul": "Любимите са изчистени",
        "gre": "Τα αγαπημένα διαγράφηκαν"
    },
    "fav_empty": {
        "eng": "No favourites yet",
        "srp": "Nema favorita",
        "bos": "Nema favorita",
        "hrv": "Nema favorita",
        "slv": "Ni priljubljenih",
        "mne": "Nema favorita",
        "mac": "Нема омилени",
        "bul": "Няма любими",
        "gre": "Δεν υπάρχουν αγαπημένα"
    },
    "fav_season": {
        "eng": "Season",
        "srp": "Sezona",
        "bos": "Sezona",
        "hrv": "Sezona",
        "slv": "Sezona",
        "mne": "Sezona",
        "mac": "Сезона",
        "bul": "Сезон",
        "gre": "Σεζόν"
    },
    "search": {
        "eng": "Search",
        "srp": "Pretraga",
        "bos": "Pretraga",
        "hrv": "Pretraživanje",
        "slv": "Iskanje",
        "mne": "Pretraga",
        "mac": "Пребарување",
        "bul": "Търсене",
        "gre": "Αναζήτηση"
    },
    "search_new": {
        "eng": "New search...",
        "srp": "Nova pretraga...",
        "bos": "Nova pretraga...",
        "hrv": "Novo pretraživanje...",
        "slv": "Novo iskanje...",
        "mne": "Nova pretraga...",
        "mac": "Ново пребарување...",
        "bul": "Ново търсене...",
        "gre": "Νέα αναζήτηση..."
    },
    "search_prompt": {
        "eng": "Title, actor, director or year",
        "srp": "Naslov, glumac, režiser ili godina",
        "bos": "Naslov, glumac, režiser ili godina",
        "hrv": "Naslov, glumac, redatelj ili godina",
        "slv": "Naslov, igralec, režiser ali leto",
        "mne": "Naslov, glumac, režiser ili godina",
        "mac": "Наслов, актер, режисер или година",
        "bul": "Заглавие, актьор, режисьор или година",
        "gre": "Τίτλος, ηθοποιός, σκηνοθέτης ή έτος"
    },
    "search_forget": {
        "eng": "Remove from search history",
        "srp": "Ukloni iz istorije pretrage",
        "bos": "Ukloni iz historije pretrage",
        "hrv": "Ukloni iz povijesti pretraživanja",
        "slv": "Odstrani iz zgodovine",
        "mne": "Ukloni iz historije pretrage",
        "mac": "Отстрани од историјата на пребарување",
        "bul": "Премахни от историята",
        "gre": "Αφαίρεση από το ιστορικό αναζήτησης"
    },
    "search_clear": {
        "eng": "Clear search history",
        "srp": "Obriši istoriju pretrage",
        "bos": "Obriši historiju pretrage",
        "hrv": "Obriši povijest pretraživanja",
        "slv": "Počisti zgodovino iskanja",
        "mne": "Obriši historiju pretrage",
        "mac": "Избриши ја историјата на пребарување",
        "bul": "Изчисти историята на търсене",
        "gre": "Εκκαθάριση ιστορικού αναζήτησης"
    },
    "search_clear_ask": {
        "eng": "Clear the whole search history?",
        "srp": "Obrisati celu istoriju pretrage?",
        "bos": "Obrisati cijelu historiju pretrage?",
        "hrv": "Obrisati cijelu povijest pretraživanja?",
        "slv": "Ali počistim celotno zgodovino?",
        "mne": "Obrisati cijelu historiju pretrage?",
        "mac": "Да ја избришам целата историја на пребарување?",
        "bul": "Да изчистя ли цялата история?",
        "gre": "Εκκαθάριση ολόκληρου του ιστορικού αναζήτησης;"
    },
    "search_none": {
        "eng": "Nothing found for",
        "srp": "Ništa nije pronađeno za",
        "bos": "Ništa nije pronađeno za",
        "hrv": "Ništa nije pronađeno za",
        "slv": "Nič ni bilo najdeno za",
        "mne": "Ništa nije pronađeno za",
        "mac": "Ништо не е пронајдено за",
        "bul": "Нищо намерено за",
        "gre": "Δεν βρέθηκε τίποτα για"
    },
    "cache_info": {
        "eng": "Cache information",
        "srp": "Informacije o kešu",
        "bos": "Informacije o kešu",
        "hrv": "Informacije o predmemoriji",
        "slv": "Informacije o predpomnilniku",
        "mne": "Informacije o kešu",
        "mac": "Информации за кешот",
        "bul": "Информация за кеша",
        "gre": "Πληροφορίες προσωρινής μνήμης"
    },
    "cache_unplaced": {
        "eng": "Outside the menu sections",
        "srp": "Van sekcija menija",
        "bos": "Van sekcija menija",
        "hrv": "Izvan odjeljaka izbornika",
        "slv": "Izven menija",
        "mne": "Van sekcija menija",
        "mac": "Надвор од секциите на менито",
        "bul": "Извън менюто",
        "gre": "Εκτός των ενοτήτων του μενού"
    },
    "cache_overlap": {
        "eng": "In more than one catalogue",
        "srp": "U više kataloga",
        "bos": "U više kataloga",
        "hrv": "U više kataloga",
        "slv": "V več katalogih",
        "mne": "U više kataloga",
        "mac": "Во повеќе каталози",
        "bul": "В повече от един каталог",
        "gre": "Σε περισσότερους από έναν καταλόγους"
    },
    "account_info": {
        "eng": "Account information",
        "srp": "Informacije o nalogu",
        "bos": "Informacije o nalogu",
        "hrv": "Informacije o računu",
        "slv": "Podatki o računu",
        "mne": "Informacije o nalogu",
        "mac": "Информации за сметката",
        "bul": "Информация за акаунта",
        "gre": "Πληροφορίες λογαριασμού"
    },
    "cache_clear": {
        "eng": "Clear cache",
        "srp": "Obriši keš",
        "bos": "Obriši keš",
        "hrv": "Obriši predmemoriju",
        "slv": "Počisti predpomnilnik",
        "mne": "Obriši keš",
        "mac": "Избриши го кешот",
        "bul": "Изчисти кеша",
        "gre": "Εκκαθάριση προσωρινής μνήμης"
    },
    "cache_clear_ask": {
        "eng": "Clear the cached catalogue? A new sync will be needed.",
        "srp": "Obrisati keširani katalog? Biće potrebna nova sinhronizacija.",
        "bos": "Obrisati keširani katalog? Biće potrebna nova sinhronizacija.",
        "hrv": "Obrisati katalog iz predmemorije? Bit će potrebna nova sinkronizacija.",
        "slv": "Ali počistim predpomnilnik? Potrebna bo nova sinhronizacija.",
        "mne": "Obrisati keširani katalog? Biće potrebna nova sinhronizacija.",
        "mac": "Да го избришам кешираниот каталог? Ќе биде потребна нова синхронизација.",
        "bul": "Да изчистя ли кеша? Ще е нужна нова синхронизация.",
        "gre": "Εκκαθάριση του αποθηκευμένου καταλόγου; Θα χρειαστεί νέος συγχρονισμός."
    },
    "cache_cleared": {
        "eng": "Cache cleared",
        "srp": "Keš je obrisan",
        "bos": "Keš je obrisan",
        "hrv": "Predmemorija je obrisana",
        "slv": "Predpomnilnik je izbrisan",
        "mne": "Keš je obrisan",
        "mac": "Кешот е избришан",
        "bul": "Кешът е изчистен",
        "gre": "Η προσωρινή μνήμη διαγράφηκε"
    },
    "no_cache": {
        "eng": "Nothing is cached yet",
        "srp": "Keš je prazan",
        "bos": "Keš je prazan",
        "hrv": "Predmemorija je prazna",
        "slv": "Brez predpomnjenih podatkov",
        "mne": "Keš je prazan",
        "mac": "Кешот е празен",
        "bul": "Няма кеширани данни",
        "gre": "Η προσωρινή μνήμη είναι κενή"
    },
    "cache_synced": {
        "eng": "Last sync",
        "srp": "Poslednja sinhronizacija",
        "bos": "Posljednja sinhronizacija",
        "hrv": "Posljednja sinkronizacija",
        "slv": "Zadnja sinhronizacija",
        "mne": "Posljednja sinhronizacija",
        "mac": "Последна синхронизација",
        "bul": "Последна синхронизация",
        "gre": "Τελευταίος συγχρονισμός"
    },
    "cache_titles": {
        "eng": "Titles",
        "srp": "Naslova",
        "bos": "Naslova",
        "hrv": "Naslova",
        "slv": "Naslovi",
        "mne": "Naslova",
        "mac": "Наслови",
        "bul": "Заглавия",
        "gre": "Τίτλοι"
    },
    "cache_series": {
        "eng": "series",
        "srp": "serija",
        "bos": "serija",
        "hrv": "serija",
        "slv": "serija",
        "mne": "serija",
        "mac": "серии",
        "bul": "сериала",
        "gre": "σειρές"
    },
    "cache_groupings": {
        "eng": "Groupings",
        "srp": "Grupacija",
        "bos": "Grupacija",
        "hrv": "Grupacija",
        "slv": "Skupina",
        "mne": "Grupacija",
        "mac": "Групации",
        "bul": "Групи",
        "gre": "Ομαδοποιήσεις"
    },
    "cache_language": {
        "eng": "Language",
        "srp": "Jezik",
        "bos": "Jezik",
        "hrv": "Jezik",
        "slv": "Jezik",
        "mne": "Jezik",
        "mac": "Јазик",
        "bul": "Език",
        "gre": "Γλώσσα"
    },
    "cache_version": {
        "eng": "Cache version",
        "srp": "Verzija keša",
        "bos": "Verzija keša",
        "hrv": "Verzija predmemorije",
        "slv": "Različica predpomnilnika",
        "mne": "Verzija keša",
        "mac": "Верзија на кешот",
        "bul": "Версия на кеша",
        "gre": "Έκδοση προσωρινής μνήμης"
    },
    "acct_host": {
        "eng": "API host",
        "srp": "API host",
        "bos": "API host",
        "hrv": "API host",
        "slv": "Gostitelj API-ja",
        "mne": "API host",
        "mac": "API хост",
        "bul": "API хост",
        "gre": "Διακομιστής API"
    },
    "acct_provider": {
        "eng": "Provider",
        "srp": "Provajder",
        "bos": "Provajder",
        "hrv": "Pružatelj usluge",
        "slv": "Ponudnik",
        "mne": "Provajder",
        "mac": "Давател на услугата",
        "bul": "Доставчик",
        "gre": "Πάροχος"
    },
    "acct_device_number": {
        "eng": "Device number (UUID)",
        "srp": "Broj uređaja (UUID)",
        "bos": "Broj uređaja (UUID)",
        "hrv": "Broj uređaja (UUID)",
        "slv": "Številka naprave (UUID)",
        "mne": "Broj uređaja (UUID)",
        "mac": "Број на уредот (UUID)",
        "bul": "Номер на устройството (UUID)",
        "gre": "Αριθμός συσκευής (UUID)"
    },
    "acct_device_id": {
        "eng": "Device ID",
        "srp": "ID uređaja",
        "bos": "ID uređaja",
        "hrv": "ID uređaja",
        "slv": "ID naprave",
        "mne": "ID uređaja",
        "mac": "ID на уредот",
        "bul": "ID на устройството",
        "gre": "Αναγνωριστικό συσκευής"
    },
    "acct_access_token": {
        "eng": "Access token expires",
        "srp": "Access token ističe",
        "bos": "Access token ističe",
        "hrv": "Pristupni token istječe",
        "slv": "Žeton poteče",
        "mne": "Access token ističe",
        "mac": "Токенот за пристап истекува",
        "bul": "Токенът изтича",
        "gre": "Το διακριτικό πρόσβασης λήγει"
    },
    "acct_refresh_token": {
        "eng": "Refresh token expires",
        "srp": "Refresh token ističe",
        "bos": "Refresh token ističe",
        "hrv": "Token za osvježavanje istječe",
        "slv": "Žeton za osvežitev poteče",
        "mne": "Refresh token ističe",
        "mac": "Токенот за освежување истекува",
        "bul": "Refresh токенът изтича",
        "gre": "Το διακριτικό ανανέωσης λήγει"
    },
    "acct_widevine": {
        "eng": "Widevine DRM",
        "srp": "Widevine DRM",
        "bos": "Widevine DRM",
        "hrv": "Widevine DRM",
        "slv": "Widevine DRM",
        "mne": "Widevine DRM",
        "mac": "Widevine DRM",
        "bul": "Widevine DRM",
        "gre": "Widevine DRM"
    },
    "cdm_installed": {
        "eng": "CDM installed",
        "srp": "CDM instaliran",
        "bos": "CDM instaliran",
        "hrv": "CDM instaliran",
        "slv": "CDM nameščen",
        "mne": "CDM instaliran",
        "mac": "CDM инсталиран",
        "bul": "CDM инсталиран",
        "gre": "CDM εγκατεστημένο"
    },
    "cdm_missing": {
        "eng": "CDM not installed",
        "srp": "CDM nije instaliran",
        "bos": "CDM nije instaliran",
        "hrv": "CDM nije instaliran",
        "slv": "CDM ni nameščen",
        "mne": "CDM nije instaliran",
        "mac": "CDM не е инсталиран",
        "bul": "CDM не е инсталиран",
        "gre": "CDM δεν είναι εγκατεστημένο"
    },
    "cdm_needed": {
        "eng": "This title needs Widevine. Install it with InputStream Helper.",
        "srp": "Ovaj naslov zahteva Widevine. Instalirajte ga preko InputStream Helper-a.",
        "bos": "Ovaj naslov zahtijeva Widevine. Instalirajte ga preko InputStream Helper-a.",
        "hrv": "Ovaj naslov zahtijeva Widevine. Instalirajte ga putem InputStream Helpera.",
        "slv": "Ta naslov potrebuje Widevine. Namestite ga z InputStream Helper.",
        "mne": "Ovaj naslov zahtijeva Widevine. Instalirajte ga preko InputStream Helper-a.",
        "mac": "Овој наслов бара Widevine. Инсталирајте го преку InputStream Helper.",
        "bul": "Това заглавие изисква Widevine. Инсталирайте го с InputStream Helper.",
        "gre": "Αυτός ο τίτλος απαιτεί Widevine. Εγκαταστήστε το με το InputStream Helper."
    },
    "drm_refused": {
        "eng": "EON did not grant a DRM licence for this title (HTTP 403). Check whether the official app plays it.",
        "srp": "EON nije izdao DRM dozvolu za ovaj naslov (HTTP 403). Proverite da li ga zvanična aplikacija pušta.",
        "bos": "EON nije izdao DRM dozvolu za ovaj naslov (HTTP 403). Provjerite da li ga zvanična aplikacija pušta.",
        "hrv": "EON nije izdao DRM dozvolu za ovaj naslov (HTTP 403). Provjerite pušta li ga službena aplikacija.",
        "slv": "EON ni izdal DRM dovoljenja za ta naslov (HTTP 403). Preverite, ali ga uradna aplikacija predvaja.",
        "mne": "EON nije izdao DRM dozvolu za ovaj naslov (HTTP 403). Provjerite da li ga zvanična aplikacija pušta.",
        "mac": "EON не издаде DRM дозвола за овој наслов (HTTP 403). Проверете дали официјалната апликација го пушта.",
        "bul": "EON не издаде DRM разрешение за това заглавие (HTTP 403). Проверете дали официалното приложение го пуска.",
        "gre": "Το EON δεν χορήγησε άδεια DRM για αυτόν τον τίτλο (HTTP 403). Ελέγξτε αν παίζει στην επίσημη εφαρμογή."
    },
    "cdm_system": {
        "eng": "CDM built into Android",
        "srp": "CDM ugrađen u Android",
        "bos": "CDM ugrađen u Android",
        "hrv": "CDM ugrađen u Android",
        "slv": "CDM vgrajen v Android",
        "mne": "CDM ugrađen u Android",
        "mac": "CDM вграден во Android",
        "bul": "CDM вграден в Android",
        "gre": "CDM ενσωματωμένο στο Android"
    },
    "expired": {
        "eng": "expired",
        "srp": "istekao",
        "bos": "istekao",
        "hrv": "istekao",
        "slv": "potekel",
        "mne": "istekao",
        "mac": "истечен",
        "bul": "изтекъл",
        "gre": "έληξε"
    },
    "unknown": {
        "eng": "unknown",
        "srp": "nepoznato",
        "bos": "nepoznato",
        "hrv": "nepoznato",
        "slv": "neznano",
        "mne": "nepoznato",
        "mac": "непознато",
        "bul": "неизвестно",
        "gre": "άγνωστο"
    },
    "yes": {
        "eng": "yes",
        "srp": "da",
        "bos": "da",
        "hrv": "da",
        "slv": "da",
        "mne": "da",
        "mac": "да",
        "bul": "да",
        "gre": "ναι"
    },
    "no": {
        "eng": "no",
        "srp": "ne",
        "bos": "ne",
        "hrv": "ne",
        "slv": "ne",
        "mne": "ne",
        "mac": "не",
        "bul": "не",
        "gre": "όχι"
    },
    "pvr_missing": {
        "eng": "pvr.eon is not installed - install and configure it first",
        "srp": "pvr.eon nije instaliran - prvo ga instalirajte i podesite",
        "bos": "pvr.eon nije instaliran - prvo ga instalirajte i podesite",
        "hrv": "pvr.eon nije instaliran - prvo ga instalirajte i podesite",
        "slv": "pvr.eon ni nameščen - najprej ga namestite in konfigurirajte",
        "mne": "pvr.eon nije instaliran - prvo ga instalirajte i podesite",
        "mac": "pvr.eon не е инсталиран - прво инсталирајте го и поставете го",
        "bul": "pvr.eon не е инсталиран - инсталирайте и настройте първо",
        "gre": "Το pvr.eon δεν είναι εγκατεστημένο - εγκαταστήστε και ρυθμίστε το πρώτα"
    },
    "pvr_not_logged_in": {
        "eng": "pvr.eon is not logged in - open Live TV once",
        "srp": "pvr.eon nije prijavljen - otvorite Live TV jednom",
        "bos": "pvr.eon nije prijavljen - otvorite Live TV jednom",
        "hrv": "pvr.eon nije prijavljen - otvorite Live TV jednom",
        "slv": "pvr.eon ni prijavljen - enkrat odprite EON TV",
        "mne": "pvr.eon nije prijavljen - otvorite Live TV jednom",
        "mac": "pvr.eon не е најавен - отворете Live TV еднаш",
        "bul": "pvr.eon не е влязъл - отворете Live TV веднъж",
        "gre": "Το pvr.eon δεν έχει συνδεθεί - ανοίξτε μία φορά την Live TV"
    },
    "pvr_no_stream_key": {
        "eng": "pvr.eon has no stream key - check the subscription",
        "srp": "pvr.eon nema stream ključ - proverite pretplatu",
        "bos": "pvr.eon nema stream ključ - provjerite pretplatu",
        "hrv": "pvr.eon nema stream ključ - provjerite pretplatu",
        "slv": "pvr.eon nima ključa za pretakanje - preverite naročnino",
        "mne": "pvr.eon nema stream ključ - provjerite pretplatu",
        "mac": "pvr.eon нема клуч за пренос - проверете ја претплатата",
        "bul": "pvr.eon няма stream ключ - проверете абонамента",
        "gre": "Το pvr.eon δεν έχει κλειδί ροής - ελέγξτε τη συνδρομή"
    },
    "available_until": {
        "eng": "Available until:",
        "srp": "Dostupno do:",
        "bos": "Dostupno do:",
        "hrv": "Dostupno do:",
        "slv": "Dostopno do:",
        "mne": "Dostupno do:",
        "mac": "Достапно до:",
        "bul": "Достъпно до:",
        "gre": "Διαθέσιμο έως:"
    },
    "sync": {
        "eng": "Sync with EON TV",
        "srp": "Sinhronizacija sa EON TV",
        "bos": "Sinhronizacija sa EON TV",
        "hrv": "Sinkronizacija s EON TV",
        "slv": "Sinhronizacija z EON TV",
        "mne": "Sinhronizacija sa EON TV",
        "mac": "Синхронизација со EON TV",
        "bul": "Синхронизация с EON TV",
        "gre": "Συγχρονισμός με το EON TV"
    },
    "sync_full": {
        "eng": "Full re-sync (slow)",
        "srp": "Potpuna sinhronizacija (sporo)",
        "bos": "Potpuna sinhronizacija (sporo)",
        "hrv": "Potpuna sinkronizacija (sporo)",
        "slv": "Popolna ponovna sinhronizacija (počasna)",
        "mne": "Potpuna sinhronizacija (sporo)",
        "mac": "Целосна синхронизација (бавно)",
        "bul": "Пълна ресинхронизация (бавно)",
        "gre": "Πλήρης επανασυγχρονισμός (αργός)"
    },
    "sync_ask": {
        "eng": "Sync is manual by default. Metadata language is English.[CR]The first sync is required; afterwards you can run it from Tools.[CR]Sync now?",
        "srp": "Sinhronizacija je podrazumevano ručna. Jezik metapodataka je srpski. Prva sinhronizacija je neophodna, a kasnije se pokreće iz Alata.[CR]Sinhronizovati sada?",
        "bos": "Sinhronizacija je podrazumijevano ručna. Jezik metapodataka je bosanski. Prva sinhronizacija je neophodna, a kasnije se pokreće iz Alata.[CR]Sinhronizovati sada?",
        "hrv": "Sinkronizacija je zadano ručna. Jezik metapodataka je hrvatski. Prva sinkronizacija je nužna, a kasnije se pokreće iz Alata.[CR]Sinkronizirati sada?",
        "slv": "Sinhronizacija je privzeto ročna. Jezik metapodatkov je slovenščina. Prva sinhronizacija je obvezna, nato jo lahko začnete v razdelku Orodja.[CR]Sinhroniziram zdaj?",
        "mne": "Sinhronizacija je podrazumijevano ručna. Jezik metapodataka je crnogorski. Prva sinhronizacija je neophodna, a kasnije se pokreće iz Alata.[CR]Sinhronizovati sada?",
        "mac": "Синхронизацијата стандардно е рачна. Јазикот на метаподатоците е македонски. Првата синхронизација е задолжителна, а подоцна се покренува од Алатки.[CR]Да синхронизирам сега?",
        "bul": "Синхронизацията е ръчна по подразбиране. Езикът на метаданните е български. Първата синхронизация е задължителна, след това може да я стартирате от Инструменти.[CR]Да синхронизирам сега?",
        "gre": "Ο συγχρονισμός γίνεται χειροκίνητα από προεπιλογή. Η γλώσσα μεταδεδομένων είναι τα ελληνικά. Ο πρώτος συγχρονισμός είναι απαραίτητος, στη συνέχεια εκτελείται από τα Εργαλεία.[CR]Συγχρονισμός τώρα;"
    },
    "sync_full_ask": {
        "eng": "A full re-sync fetches every title again and can take several minutes. The current catalogue stays usable until it finishes.[CR]Continue?",
        "srp": "Potpuna sinhronizacija ponovo preuzima sve naslove i može da potraje nekoliko minuta. Trenutni katalog ostaje upotrebljiv dok se ne završi.[CR]Nastaviti?",
        "bos": "Potpuna sinhronizacija ponovo preuzima sve naslove i može potrajati nekoliko minuta. Trenutni katalog ostaje upotrebljiv dok se ne završi.[CR]Nastaviti?",
        "hrv": "Potpuna sinkronizacija ponovno preuzima sve naslove i može potrajati nekoliko minuta. Trenutni katalog ostaje upotrebljiv dok ne završi.[CR]Nastaviti?",
        "slv": "Popolna ponovna sinhronizacija prenese vse naslove in lahko traja nekaj minut. Trenutni katalog ostane uporaben, dokler ni dokončan.[CR]Želite nadaljevati?",
        "mne": "Potpuna sinhronizacija ponovo preuzima sve naslove i može potrajati nekoliko minuta. Trenutni katalog ostaje upotrebljiv dok se ne završi.[CR]Nastaviti?",
        "mac": "Целосната синхронизација повторно ги презема сите наслови и може да трае неколку минути. Тековниот каталог останува употреблив додека не заврши.[CR]Да продолжам?",
        "bul": "Пълната ресинхронизация изтегля наново всички заглавия и може да отнеме няколко минути. Текущият каталог остава използваем, докато приключи.[CR]Да продължа ли?",
        "gre": "Ο πλήρης επανασυγχρονισμός κατεβάζει ξανά όλους τους τίτλους και μπορεί να διαρκέσει αρκετά λεπτά. Ο τρέχων κατάλογος παραμένει διαθέσιμος μέχρι να ολοκληρωθεί.[CR]Συνέχεια;"
    },
    "age_blocked": {
        "eng": "Blocked by the age limit:",
        "srp": "Blokirano uzrasnim ograničenjem:",
        "bos": "Blokirano uzrasnim ograničenjem:",
        "hrv": "Blokirano dobnim ograničenjem:",
        "slv": "Blokirano zaradi starostne omejitve:",
        "mne": "Blokirano uzrasnim ograničenjem:",
        "mac": "Блокирано со возрасно ограничување:",
        "bul": "Блокирано от възрастовото ограничение:",
        "gre": "Αποκλεισμένο από το όριο ηλικίας:"
    },
    "age_unrated": {
        "eng": "No age rating, blocked while a limit is set.",
        "srp": "Nema uzrasne oznake, blokirano uz ograničenje.",
        "bos": "Nema uzrasne oznake, blokirano uz ograničenje.",
        "hrv": "Nema dobne oznake, blokirano uz ograničenje.",
        "slv": "Brez starostne omejitve, blokirano pod omejitvami.",
        "mne": "Nema uzrasne oznake, blokirano uz ograničenje.",
        "mac": "Нема возрасна ознака, блокирано додека има ограничување.",
        "bul": "Няма възрастова оценка, блокирано при ограничение.",
        "gre": "Χωρίς ηλικιακή διαβάθμιση, αποκλεισμένο όσο ισχύει όριο."
    },
}


def tr(key: str) -> str:
    lang = metadata_language()
    return TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("eng", key))


def media_icon(name: str) -> str:
    return xbmcvfs.translatePath(ADDON_PATH + f"/resources/media/{name}.png")


def addon_icon() -> str:
    return xbmcvfs.translatePath(ADDON_PATH + "/icon.png")


def first_image(images: list[dict[str, Any]] | None, preferred: tuple[str, ...]) -> str:
    if not images:
        return ""

    def pick(candidates: list[dict[str, Any]]) -> str:
        path = ""
        for image in candidates:
            candidate = image.get("path") or ""
            if not candidate:
                continue
            if image.get("size") == "XL":
                return image_url(candidate)
            if not path:
                path = candidate
        return image_url(path) if path else ""

    for wanted in preferred:
        found = pick([img for img in images if isinstance(img, dict) and img.get("type") == wanted])
        if found:
            return found
    return pick([img for img in images if isinstance(img, dict)])


CATALOGUE_IMAGE_TYPES = (
    "VOD_POSTER_2_3",
    "VOD_POSTER_21_31",
    "EVENT_16_9",
    "STB_XL",
    "APPLICATION",
    "CATALOGUE_MESSAGE_ICON_LARGE",
    "CATALOGUE_MESSAGE_ICON_SMALL",
)


def catalogue_images(images: list[dict[str, Any]] | None) -> list[str]:
    out: list[str] = []
    if not images:
        return out
    for wanted in CATALOGUE_IMAGE_TYPES:
        found = first_image(images, (wanted,))

        if found and any(isinstance(img, dict) and img.get("type") == wanted for img in images):
            if found not in out:
                out.append(found)
    rest = first_image(images, ())
    if rest and rest not in out:
        out.append(rest)
    return out


def catalogue_image(images: list[dict[str, Any]] | None) -> str:
    candidates = catalogue_images(images)
    return candidates[0] if candidates else ""


def item_title(item: dict[str, Any]) -> str:
    content_type = item.get("contentType") or item.get("vodType")
    title = str(item.get("title") or "").strip()
    if item.get("episodeNumber") is not None:
        episode_title = str(item.get("episodeTitle") or "").strip()
        if episode_title:
            title = episode_title
    if not title:
        title = item.get("episodeTitle") or item.get("seriesTitle") or item.get("originalTitle")
    title = str(title or "").strip()
    word = episode_word()
    if content_type == "EPISODE" and title and item.get("episodeNumber") \
            and word.casefold() not in title.casefold():
        title = f"{word} {item.get('episodeNumber')}: {title}"
    if title:
        return title
    episode = item.get("episodeNumber")
    if episode:
        return f"{word} {episode}"

    slug = (item.get("slug") or "").strip()
    if slug:
        return slug.replace("-", " ").replace("_", " ").strip().title()
    return f"VOD {item.get('id', '')}".strip()


def set_resolved_failed(message: str) -> None:
    notify(message)
    xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())


@dataclass
class PvrSettings:
    access_token: str
    device_id: str
    device_number: str
    stream_key: str
    stream_user: str
    provider: str
    generic_access_token: str
    refresh_token: str


class EonApi:
    def __init__(self) -> None:
        self.pvr_addon = self._open_pvr_addon()
        self.settings = self._read_settings()
        self._servers: list[dict[str, Any]] | None = None
        self._asset_details: dict[str, dict[str, Any]] = {}

        self._vod_details: dict[str, dict[str, Any]] = {}
        self._sp: dict[str, Any] | None = None
        self._profiles: dict[int, dict[str, Any]] | None = None
        self._catalogues: list[dict[str, Any]] | None = None
        self._ctime_offset: float | None = None
        self._token_lock = threading.Lock()

        self.cdn_identifier = ""

        cached = load_session(self.settings)
        if cached:
            self._apply_session(cached)
        else:
            self._resolve_base_api()
        self.ensure_access_token()

    def _open_pvr_addon(self) -> xbmcaddon.Addon | None:
        try:
            return xbmcaddon.Addon(PVR_ADDON_ID)
        except RuntimeError:
            return None

    def _pvr_version(self) -> tuple[int, ...]:
        raw = ""
        if self.pvr_addon is not None:
            try:
                raw = self.pvr_addon.getAddonInfo("version") or ""
            except Exception:
                raw = ""

        if not raw:
            path = xbmcvfs.translatePath(f"special://home/addons/{PVR_ADDON_ID}/addon.xml")
            if xbmcvfs.exists(path):
                try:
                    import xml.etree.ElementTree as ET

                    raw = ET.parse(path).getroot().get("version") or ""
                except Exception as exc:
                    log(f"Could not read pvr.eon's version from addon.xml: {exc}",
                        xbmc.LOGWARNING)

        if not raw:
            return ()

        parts: list[int] = []
        for chunk in raw.split("."):
            digits = ""
            for ch in chunk:
                if not ch.isdigit():
                    break
                digits += ch
            if not digits:
                break
            parts.append(int(digits))
        return tuple(parts)

    def _provider_brand_map(self) -> tuple[dict[str, str], bool]:
        version = self._pvr_version()
        if not version:
            log("Could not determine pvr.eon's version; assuming its current provider list",
                xbmc.LOGWARNING)
            return PROVIDER_BRAND_IDENTIFIERS, False

        if version < PROVIDER_LIST_CHANGED_IN:
            log(f"pvr.eon {'.'.join(str(p) for p in version)} predates the provider list "
                f"change; reading its setting with the old index meanings")
            return LEGACY_PROVIDER_BRAND_IDENTIFIERS, True

        return PROVIDER_BRAND_IDENTIFIERS, False

    def _setting(self, key: str) -> str:
        if self.pvr_addon is not None:
            value = self.pvr_addon.getSetting(key)
            if value:
                return value

        profile = xbmcvfs.translatePath(
            f"special://profile/addon_data/{PVR_ADDON_ID}/settings.xml")
        if not xbmcvfs.exists(profile):
            return ""

        try:
            import xml.etree.ElementTree as ET

            root = ET.parse(profile).getroot()
            for node in root.findall("setting"):
                if node.get("id") == key:
                    return node.get("value") or node.text or ""
        except Exception as exc:
            log(f"Failed to read pvr.eon setting {key}: {exc}", xbmc.LOGWARNING)
        return ""

    def _read_settings(self) -> PvrSettings:
        return PvrSettings(
            access_token=self._setting("accesstoken"),
            device_id=self._setting("deviceid"),
            device_number=self._setting("devicenumber"),
            stream_key=self._setting("streamkey"),
            stream_user=self._setting("streamuser"),
            provider=self._setting("provider"),
            generic_access_token=self._setting("genericaccesstoken"),
            refresh_token=self._setting("refreshtoken"),
        )

    def _write_pvr_setting(self, key: str, value: str) -> None:
        if self.pvr_addon is None or not value:
            return
        try:
            self.pvr_addon.setSetting(key, value)
        except Exception as exc:
            log(f"Could not write pvr.eon setting {key}: {exc}", xbmc.LOGWARNING)

    def ensure_access_token(self, force: bool = False) -> None:
        if not force and not self._is_token_expired(self.settings.access_token):
            return

        stale = self.settings.access_token
        with self._token_lock:
            if self.settings.access_token != stale:
                return
            self._refresh_access_token()

    def _refresh_access_token(self) -> None:
        refresh_token = self.settings.refresh_token
        if not refresh_token:
            log("Access token expired and no refresh token available - open Live TV once to re-login",
                xbmc.LOGWARNING)
            return

        basic = base64.b64encode(
            f"{WEB_CLIENT_ID}:{WEB_CLIENT_SECRET}".encode("ascii")
        ).decode("ascii")
        url = API + "oauth/token?grant_type=refresh_token&refresh_token=" + quote(refresh_token, safe="")
        request = Request(
            url,
            data=b"{}",
            headers={
                "User-Agent": user_agent(),
                "Authorization": "Basic " + basic,
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=25) as response:
                data = json.loads(response.read().decode("utf-8") or "{}")
        except Exception as exc:
            log(f"Access token refresh failed: {exc}", xbmc.LOGERROR)
            return

        access_token = data.get("access_token") or ""
        if not access_token:
            log("Access token refresh returned no token", xbmc.LOGERROR)
            return

        self.settings.access_token = access_token
        self._write_pvr_setting("accesstoken", access_token)

        for key, field in (
            ("refreshtoken", "refresh_token"),
            ("streamkey", "stream_key"),
            ("streamuser", "stream_un"),
            ("devicenumber", "device_number"),
        ):
            value = data.get(field) or ""
            if value:
                self._write_pvr_setting(key, value)
                if field == "refresh_token":
                    self.settings.refresh_token = value
                elif field == "stream_key":
                    self.settings.stream_key = value
                elif field == "stream_un":
                    self.settings.stream_user = value
                elif field == "device_number":
                    self.settings.device_number = value

        log("Access token refreshed by the VOD plugin")

    def _is_token_expired(self, token: str) -> bool:
        if not token:
            return True
        try:
            payload_segment = token.split(".")[1]
            payload_segment += "=" * (-len(payload_segment) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_segment))
            exp = payload.get("exp")
            return exp is None or time.time() >= exp
        except Exception:
            return True

    def _apply_session(self, data: dict[str, Any]) -> None:
        global API, IMAGES
        API = data.get("api") or API
        IMAGES = data.get("images") or IMAGES
        if data.get("sp"):
            self._sp = data["sp"]
        if data.get("profiles"):
            self._profiles = {int(k): v for k, v in data["profiles"].items()}
        self._ctime_offset = data.get("ctime_offset")
        if data.get("servers"):
            self._servers = data["servers"]
        self.cdn_identifier = data.get("cdn") or ""

    def store_session(self) -> None:
        save_session(self.settings, {
            "api": API,
            "images": IMAGES,
            "sp": self._sp or {},
            "profiles": {str(k): v for k, v in (self._profiles or {}).items()},
            "ctime_offset": self._ctime_offset,
            "servers": self._servers or [],
            "cdn": self.cdn_identifier,
        })

    def _basic_auth(self) -> str:
        return "Basic " + base64.b64encode(
            f"{WEB_CLIENT_ID}:{WEB_CLIENT_SECRET}".encode("ascii")
        ).decode("ascii")

    def _mint_generic_token(self) -> str:
        request = Request(
            BROKER_URL + "oauth/token?grant_type=client_credentials",
            data=b"",
            headers={"User-Agent": user_agent(), "Authorization": self._basic_auth()},
        )
        try:
            with urlopen(request, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8") or "{}")
        except Exception as exc:
            log(f"Could not mint a generic access token: {exc}", xbmc.LOGERROR)
            return ""
        token = data.get("access_token") or ""
        if token:
            self.settings.generic_access_token = token
            self._write_pvr_setting("genericaccesstoken", token)
            log("Minted a fresh generic access token for the broker", xbmc.LOGDEBUG)
        return token

    def _broker_get(self, path: str) -> Any:
        headers = self.headers(auth=False)
        token = self.settings.generic_access_token
        if self._is_token_expired(token):
            token = self._mint_generic_token()
        if not token:
            raise RuntimeError("no generic access token available for the broker")
        headers["Authorization"] = "bearer " + token

        request = Request(BROKER_URL + path, headers=headers)
        with urlopen(request, timeout=15) as response:
            data = response.read().decode("utf-8")
        return json.loads(data) if data else None

    def _sp_id_from_token(self) -> str:
        token = self.settings.access_token
        try:
            payload_segment = token.split(".")[1]
            payload_segment += "=" * (-len(payload_segment) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_segment))
            sp_id = payload.get("sp_id")
            return str(sp_id) if sp_id is not None else ""
        except Exception as exc:
            log(f"Could not decode sp_id from accesstoken: {exc}", xbmc.LOGWARNING)
            return ""

    def _resolve_base_api(self) -> None:
        global API, IMAGES

        provider_setting = self.settings.provider
        try:
            provider_index = int(provider_setting)
        except (TypeError, ValueError):
            provider_index = -1
        token_sp_id = self._sp_id_from_token()
        if token_sp_id:
            log(f"pvr.eon provider setting={provider_setting}, account token sp_id={token_sp_id}")
        try:
            brands = self._broker_get("v2/brands") or []
            cdns = self._broker_get("v1/cdninfo") or []
        except Exception as exc:
            log(f"Failed to resolve brand/base API, falling back to the UG host - this is only correct "
                f"for SBB/Telemach accounts and will show the wrong catalogue for others: {exc}",
                xbmc.LOGERROR)
            return

        cdn_identifier = ""
        matched_by = ""
        brand_map, legacy_mapping = self._provider_brand_map()
        expected_identifier = brand_map.get(str(provider_setting), "")

        for brand in brands:
            if expected_identifier and brand.get("identifier") == expected_identifier:
                cdn_identifier = brand.get("cdnIdentifier") or ""
                matched_by = f"brand identifier '{expected_identifier}'"
                break

        if not cdn_identifier and legacy_mapping and 0 <= provider_index < len(brands):
            cdn_identifier = brands[provider_index].get("cdnIdentifier") or ""
            matched_by = f"position {provider_index} ('{brands[provider_index].get('identifier')}')"
            log(f"pvr.eon setting {provider_setting} has no brand identifier of its own in that "
                f"version; matched by position against {[b.get('identifier') for b in brands]}",
                xbmc.LOGWARNING)
        elif not cdn_identifier and expected_identifier:
            log(f"Brand identifier '{expected_identifier}' was not among the broker's brands "
                f"{[b.get('identifier') for b in brands]}; using the broker's default CDN",
                xbmc.LOGWARNING)

        chosen = next((c for c in cdns if c.get("identifier") == cdn_identifier), None)
        if chosen is None:
            chosen = next((c for c in cdns if c.get("isDefault")), None) or (cdns[0] if cdns else None)
            if chosen is not None:
                log(
                    f"Brand setting {provider_setting} could not be matched against the broker's "
                    f"{len(brands)} brands; using its default CDN "
                    f"({chosen.get('identifier')}). Correct for the ex-Yu brands, which share "
                    f"one CDN. If this account's catalogue is in the wrong language, this line "
                    f"is why - send it in with the brands the broker returned: "
                    f"{[b.get('identifier') for b in brands]}",
                    xbmc.LOGWARNING,
                )

        if chosen is None:
            log("The broker returned no CDN information at all; keeping the built-in host",
                xbmc.LOGERROR)
            return

        base_map = ((chosen.get("domains") or {}).get("baseApi") or {})
        base_api = base_map.get(API_SELECTOR) or next(iter(base_map.values()), "")

        if not base_api:
            log(
                f"CDN '{chosen.get('identifier')}' publishes no API host; keeping the built-in one",
                xbmc.LOGERROR,
            )
            return

        API = f"https://api-web.{base_api}/"
        IMAGES = f"https://images-web.{base_api}"
        self.cdn_identifier = str(chosen.get("identifier") or "")
        log(f"Resolved brand '{chosen.get('identifier')}' -> API host {API}"
            + (f" (matched by {matched_by})" if matched_by else " (broker default)"))
        self.store_session()

    def headers(self, auth: bool = True) -> dict[str, str]:
        headers = {
            "User-Agent": user_agent(),
            "Accept": "application/json, text/plain, */*",
            "X-UCP-TIME-FORMAT": "timestamp",
            "X-Ucp-Language": metadata_language(),
            "X-Ucp-Theme-Mode": "ALL",
            "Origin": "https://eon.tv",
            "Referer": "https://eon.tv/",
        }
        if auth and self.settings.access_token:
            headers["Authorization"] = "bearer " + self.settings.access_token
        return headers

    def vod_detail(self, asset_id: Any) -> dict[str, Any]:
        key = str(asset_id)
        if key in self._vod_details:
            return self._vod_details[key]
        data = self.get_json(f"v1/vodassets/{key}")
        if data:
            self._vod_details[key] = data
        return data

    def get_json(self, path: str, params: dict[str, Any] | None = None,
                 _retried: bool = False) -> Any:
        url = API + path.lstrip("/")
        if params:
            url += "?" + urlencode(params, doseq=True)
        request = Request(url, headers=self.headers())
        try:
            with urlopen(request, timeout=25) as response:
                data = response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 401 and not _retried:
                log(f"HTTP 401 from {url} - refreshing the access token and retrying once",
                    xbmc.LOGWARNING)
                self.ensure_access_token(force=True)
                return self.get_json(path, params, _retried=True)
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            log(
                f"HTTP {exc.code} from {url} - reason={exc.reason} body={body[:1000]}",
                xbmc.LOGERROR,
            )
            raise
        except URLError as exc:
            log(f"Network error calling {url}: {exc.reason}", xbmc.LOGERROR)
            raise
        return json.loads(data) if data else None

    def servers(self) -> list[dict[str, Any]]:
        if self._servers is None:
            data = self.get_json("v1/servers")
            self._servers = (data.get("vod_servers") or data.get("timeshift_servers")
                             or data.get("live_servers") or [])
            if self._servers:
                self.store_session()
        return self._servers

    def time(self) -> str:
        now = time.time() * 1000.0
        if self._ctime_offset is None:
            try:
                served = int((self.get_json("v1/time") or {}).get("time") or 0)
            except Exception as exc:
                log(f"Could not read the server clock: {exc}", xbmc.LOGWARNING)
                served = 0
            if served:
                self._ctime_offset = served - now
                self.store_session()
        if self._ctime_offset is None:
            return str(int(now))
        return str(int(now + self._ctime_offset))

    def catalogues(self) -> list[dict[str, Any]]:
        if self._catalogues is None:
            try:
                self._catalogues = [
                    cat for cat in (self.get_json("v1/catalogues") or []) if (cat or {}).get("id")
                ]
            except Exception as exc:
                log(f"Could not fetch v1/catalogues: {exc}", xbmc.LOGERROR)
                self._catalogues = []
        return self._catalogues

    def _service_provider(self) -> dict[str, Any]:
        if self._sp is None:
            try:
                self._sp = self.get_json("v1/sp") or {}
            except Exception as exc:
                log(f"Could not fetch v1/sp: {exc}", xbmc.LOGERROR)
                self._sp = {}
            else:
                self.store_session()
        return self._sp

    def service_provider_id(self) -> str:
        sp = self._service_provider()
        return str(sp.get("identifier") or sp.get("id") or "")

    def widevine_url(self) -> str:
        return str(self._service_provider().get("licenseServerUrlWidewine") or "")

    def profiles(self) -> dict[int, dict[str, Any]]:
        if self._profiles is None:
            self._profiles = {}
            try:
                for prof in self.get_json("v1/rndprofiles") or []:
                    pid = prof.get("id")
                    if pid is not None:
                        self._profiles[int(pid)] = {
                            "core_stream_id": prof.get("coreStreamId") or "",
                            "video_bitrate": int(prof.get("videoBitrate") or 0),
                        }
            except Exception as exc:
                log(f"Could not fetch v1/rndprofiles: {exc}", xbmc.LOGERROR)
            else:
                self.store_session()
        return self._profiles

    def vod_pre_auth(self, publishing_point: str) -> str:
        base = API.replace("api-web.", "entitlement-web.")
        url = base + "v1/drm/preAuthTokenVod"
        request = Request(
            url,
            data=json.dumps({"vodPublishingPoint": publishing_point, "mode": "STREAMING"}).encode("utf-8"),
            headers=dict(self.headers(), **{"Content-Type": "application/json"}),
        )
        try:
            with urlopen(request, timeout=25) as response:
                data = json.loads(response.read().decode("utf-8") or "{}")
        except HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                pass
            log(f"No DRM pre-authorization for this title: HTTP {exc.code} from {url} "
                f"point={publishing_point} body={body[:500]}", xbmc.LOGWARNING)
            return ""
        except Exception as exc:
            log(f"No DRM pre-authorization for this title: {exc} (url={url} "
                f"point={publishing_point})", xbmc.LOGWARNING)
            return ""
        return str(data.get("preAuthToken") or "")

    def stream_url(self, asset_id: str) -> tuple[str, str]:
        asset = self.vod_detail(asset_id)
        points = asset.get("publishingPoint") or []
        if not points:
            raise RuntimeError("This VOD item has no publishing point")

        point = points[0]
        publishing_point = str(point.get("publishingPoint") or "")
        cfgs = point.get("playerCfgs") or []
        cfg = next((cfg for cfg in cfgs if cfg.get("type") == "vod"), cfgs[0] if cfgs else {})
        sig = cfg.get("sig") or ""

        profiles = self.profiles()
        best = None
        for pid in point.get("profileIds") or []:
            profile = profiles.get(int(pid)) if str(pid).isdigit() else None
            if profile and (best is None or profile["video_bitrate"] > best["video_bitrate"]):
                best = profile
        if not best:
            raise RuntimeError("No rendering profile for this title is playable by this account")

        provider = self.service_provider_id()
        if not provider:
            raise RuntimeError("Could not resolve the service provider identifier")

        server = self._select_vod_server()
        session = str(uuid.uuid4())

        plain = (
            f"asset={publishing_point};"
            f"stream={best['core_stream_id']};"
            f"sp={provider};"
            f"u={self.settings.stream_user};"
            f"ss={self.settings.stream_key};"

            f"minvbr={min(100, int(best.get('video_bitrate') or 0))};"
            "adaptive=true;"
            f"player={PLAYER_VOD};"
            f"sig={sig};"
            f"session={session};"
            f"m={server.get('ip')};"
            f"device={self.settings.device_number};"
            f"ctime={self.time()};"
            f"conn={CONN_TYPE};"
            "aa=false"
        )

        iv = os.urandom(16)
        key = b64url_decode(self.settings.stream_key)
        encrypted = aes_cbc_pkcs7_encrypt(key, iv, plain.encode("utf-8"))
        url = (
            f"https://{server.get('hostname')}/stream?"
            + urlencode(
                {
                    "i": b64url_encode(iv),
                    "a": b64url_encode(encrypted),
                    "sp": provider,
                    "u": self.settings.stream_user,
                    "player": PLAYER_VOD,
                    "session": session,
                    "sig": sig,
                    "lang": STREAM_LANG,
                    "nofps-info": STREAM_NOFPS_INFO,
                }
            )
        )
        log(
            f"Prepared VOD stream asset={asset_id} sp={provider} profile={best['core_stream_id']} "
            f"server={server.get('id')} host={server.get('hostname')}",
            xbmc.LOGDEBUG,
        )
        return url, publishing_point

    def _select_vod_server(self) -> dict[str, Any]:
        servers = self.servers()
        if not servers:
            raise RuntimeError("No VOD servers returned by EON")
        for server in servers:
            server_id = str(server.get("id") or "").upper()
            hostname = str(server.get("hostname") or "").lower()
            if "EDGE" in server_id or "-edge" in hostname:
                return server
        return servers[0]

    def probe_stream_url(self, url: str) -> str:
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": user_agent(),
                    "Accept": "application/vnd.apple.mpegurl, application/x-mpegURL, */*",
                    "Origin": "https://eon.tv",
                    "Referer": "https://eon.tv/",
                },
            )
            with urlopen(request, timeout=15) as response:
                sample = response.read(512)
                final = urlparse(response.geturl())
                content_type = response.headers.get("content-type", "")
                text = sample.decode("utf-8", "replace").replace("\n", "\\n")
                log(
                    "VOD stream probe "
                    f"status={response.status} final_host={final.hostname} "
                    f"content_type={content_type} sample={text[:120]}",
                    xbmc.LOGDEBUG,
                )
                return sample.decode("utf-8", "replace")
        except HTTPError as exc:
            sample = exc.read(180).decode("utf-8", "replace").replace("\n", "\\n")
            final = urlparse(exc.url or url)
            log(
                "VOD stream probe failed "
                f"status={exc.code} final_host={final.hostname} reason={exc.reason} sample={sample[:120]}",
                xbmc.LOGERROR,
            )

            if exc.code != 403:
                return ""
            reason = ""
            for part in sample.replace("<", ">").split(">"):
                if "403." in part:
                    reason = part.strip()
                    break
            if "2700" in reason or "6500" in reason:
                raise RuntimeError(
                    f"EON has no recording for this title - it is listed in the catalogue but "
                    f"their server does not serve it ({reason or '403'}). Not a subscription "
                    f"problem and not fixable from this side."
                )
            raise RuntimeError(f"EON refused this title ({reason or '403'}).")
        except URLError as exc:
            log(f"VOD stream probe failed url_error={exc.reason}", xbmc.LOGERROR)
        except Exception as exc:
            log(f"VOD stream probe failed: {exc}", xbmc.LOGERROR)
        return ""


def b64url_decode(value: str) -> bytes:
    value = value.replace("-", "+").replace("_", "/")
    value += "=" * ((4 - len(value) % 4) % 4)
    return base64.b64decode(value)


def b64url_encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii").replace("+", "-").replace("/", "_").rstrip("=")


def aes_cbc_pkcs7_encrypt(key: bytes, iv: bytes, payload: bytes) -> bytes:
    mode = pyaes.AESModeOfOperationCBC(key, iv=iv)
    encrypter = pyaes.Encrypter(mode, padding=pyaes.PADDING_DEFAULT)
    return encrypter.feed(payload) + encrypter.feed()

_favorites_memo: list[dict[str, Any]] | None = None


def session_fingerprint(settings: "PvrSettings") -> str:
    raw = f"{settings.device_number}|{settings.stream_user}|{metadata_language()}"
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")[:24]


def load_session(settings: "PvrSettings") -> dict[str, Any] | None:
    if not xbmcvfs.exists(SESSION_FILE):
        return None
    try:
        handle = xbmcvfs.File(SESSION_FILE, "r")
        try:
            data = json.loads(handle.read() or "{}")
        finally:
            handle.close()
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    if data.get("account") != session_fingerprint(settings):
        return None
    if time.time() >= (data.get("expires_at") or 0):
        return None
    if not data.get("api"):
        return None
    if "cdn" not in data:
        return None
    return data


def save_session(settings: "PvrSettings", payload: dict[str, Any]) -> None:
    try:
        ensure_addon_data()
        payload = dict(payload)
        payload["account"] = session_fingerprint(settings)
        payload["expires_at"] = time.time() + SESSION_MAX_AGE
        handle = xbmcvfs.File(SESSION_FILE, "w")
        try:
            handle.write(json.dumps(payload, ensure_ascii=False))
        finally:
            handle.close()
    except Exception as exc:
        log(f"Could not cache the session: {exc}", xbmc.LOGWARNING)

_playback_memo: dict[str, dict[str, float]] | None = None


def load_playback() -> dict[str, dict[str, float]]:
    global _playback_memo
    if _playback_memo is not None:
        return _playback_memo
    _playback_memo = {}
    if not xbmcvfs.exists(PLAYBACK_FILE):
        return _playback_memo
    handle = None
    try:
        handle = xbmcvfs.File(PLAYBACK_FILE, "r")
        data = json.loads(handle.read() or "{}")
        if isinstance(data, dict):
            _playback_memo = {k: v for k, v in data.items() if isinstance(v, dict)}
    except Exception as exc:
        log(f"Could not read the playback state: {exc}", xbmc.LOGWARNING)
    finally:
        if handle is not None:
            handle.close()
    return _playback_memo


def resume_point(asset_id: Any) -> tuple[float, float]:
    entry = load_playback().get(str(asset_id)) or {}
    return float(entry.get("position") or 0), float(entry.get("total") or 0)


def provider_progress(asset: dict[str, Any]) -> tuple[int, float]:
    watched = 1 if asset.get("watched") is True else 0
    try:
        progress = float(asset.get("watchProgress") or 0)
    except (TypeError, ValueError):
        progress = 0.0

    runtime = runtime_seconds(asset)
    if not (runtime and RESUME_MIN_SECONDS <= progress < runtime * RESUME_DONE_FRACTION):
        progress = 0.0
    return watched, progress


def watch_count(asset_id: Any) -> int:
    entry = load_playback().get(str(asset_id)) or {}
    try:
        return int(entry.get("watched") or 0)
    except (TypeError, ValueError):
        return 0


def remember_episode_parent(api: "EonApi", asset_id: str) -> None:
    try:
        detail = api.vod_detail(asset_id) or {}
    except Exception:
        return
    if detail.get("episodeNumber") is None or not detail.get("seriesId"):
        return
    try:
        window = xbmcgui.Window(HOME_WINDOW)
        window.setProperty(PLAYING_SERIES_PROPERTY, str(detail["seriesId"]))
        season = detail.get("seasonNumber")
        window.setProperty(PLAYING_SEASON_PROPERTY, "" if season is None else str(season))
        log(f"Episode {asset_id} belongs to series {detail['seriesId']} season {season}",
            xbmc.LOGDEBUG)
    except Exception as exc:
        log(f"Could not publish the episode's series: {exc}", xbmc.LOGWARNING)


def watched_episodes(series_id: Any, season: Any = None) -> int:
    wanted = str(series_id)
    total = 0
    for entry in load_playback().values():
        if not isinstance(entry, dict) or not entry.get("watched"):
            continue
        if str(entry.get("series") or "") != wanted:
            continue
        if season is not None and str(entry.get("season")) != str(season):
            continue
        total += 1
    return total


def season_watched(episodes: list[dict[str, Any]] | None) -> bool:
    ids = [str(ep.get("id")) for ep in episodes or [] if isinstance(ep, dict) and ep.get("id")]
    return bool(ids) and all(watch_count(episode_id) for episode_id in ids)


def series_watched(asset: dict[str, Any]) -> bool:
    try:
        total = int(asset.get("episodeCount") or 0)
    except (TypeError, ValueError):
        total = 0
    return total > 0 and watched_episodes(asset.get("id")) >= total


def load_searches() -> list[str]:
    if not xbmcvfs.exists(SEARCHES_FILE):
        return []
    try:
        handle = xbmcvfs.File(SEARCHES_FILE, "r")
        try:
            data = json.loads(handle.read() or "[]")
        finally:
            handle.close()
        return [q for q in data if isinstance(q, str) and q.strip()][:MAX_SEARCH_HISTORY]
    except Exception as exc:
        log(f"Could not read search history: {exc}", xbmc.LOGWARNING)
        return []


def save_searches(queries: list[str]) -> None:
    try:
        ensure_addon_data()
        handle = xbmcvfs.File(SEARCHES_FILE, "w")
        try:
            handle.write(json.dumps(queries[:MAX_SEARCH_HISTORY], ensure_ascii=False))
        finally:
            handle.close()
    except Exception as exc:
        log(f"Could not write search history: {exc}", xbmc.LOGERROR)


def remember_search(query: str) -> None:
    query = query.strip()
    if not query:
        return
    history = [q for q in load_searches() if q.casefold() != query.casefold()]
    history.insert(0, query)
    save_searches(history)


def favorite_key(kind: str, item_id: Any, season: Any = None) -> str:
    if kind == "season":
        return f"season:{item_id}:{season}"
    return f"{kind}:{item_id}"


def load_favorites() -> list[dict[str, Any]]:
    global _favorites_memo
    if _favorites_memo is not None:
        return _favorites_memo
    _favorites_memo = []
    if xbmcvfs.exists(FAVORITES_FILE):
        try:
            handle = xbmcvfs.File(FAVORITES_FILE, "r")
            try:
                data = json.loads(handle.read() or "[]")
            finally:
                handle.close()
            if isinstance(data, list):
                _favorites_memo = [entry for entry in data if isinstance(entry, dict) and entry.get("key")]
        except Exception as exc:
            log(f"Could not read favourites: {exc}", xbmc.LOGWARNING)
    return _favorites_memo


def ensure_addon_data() -> None:
    if not xbmcvfs.exists(ADDON_DATA):
        xbmcvfs.mkdirs(ADDON_DATA)


def drop_legacy_cache() -> None:
    try:
        if xbmcvfs.exists(LEGACY_CACHE_FILE):
            xbmcvfs.delete(LEGACY_CACHE_FILE)
            log("Removed the legacy cache from pvr.eon's addon data directory")
    except Exception as exc:
        log(f"Could not remove the legacy cache: {exc}", xbmc.LOGWARNING)


def save_favorites(entries: list[dict[str, Any]]) -> None:
    global _favorites_memo
    _favorites_memo = entries
    try:
        ensure_addon_data()
        handle = xbmcvfs.File(FAVORITES_FILE, "w")
        try:
            handle.write(json.dumps(entries, ensure_ascii=False))
        finally:
            handle.close()
    except Exception as exc:
        log(f"Could not write favourites: {exc}", xbmc.LOGERROR)


def favorite_keys() -> set[str]:
    return {entry.get("key") for entry in load_favorites()}


def is_favorite(kind: str, item_id: Any, season: Any = None) -> bool:
    return favorite_key(kind, item_id, season) in favorite_keys()

MENU_COLOUR_FAVORITES = "FFFFD000"
MENU_COLOUR_SEARCH = "FFFF7A00"
MENU_COLOUR_TOOLS = "FF00A8FF"

MUTED_COLOUR = "FF8A8A8A"

FAVORITE_COLOUR = MENU_COLOUR_FAVORITES
EXPIRED_COLOUR = "firebrick"

PAGING_COLOUR = "FF7FC4C4"


def is_expired(asset: dict[str, Any]) -> bool:
    try:
        stamp = int(asset.get("expirationDate") or 0) / 1000
    except (TypeError, ValueError):
        return False
    return 0 < stamp < time.time()


def favorite_snapshot(asset: dict[str, Any], kind: str) -> dict[str, Any]:
    keep = ("id", "title", "originalTitle", "contentType", "vodType", "year", "firstYear",
            "duration", "adGenres", "country", "people", "assetRatings", "ageRating",
            "mediaQuality", "expirationDate", "longDescription", "shortDescription",
            "images", "seriesTitle", "seasonNumber", "episodeNumber", "publishingPoint",
            "memberships", "categoryIds", "catalogueIds")
    snapshot = {field: asset.get(field) for field in keep if asset.get(field) not in (None, "", [])}
    snapshot["kind"] = kind
    return snapshot


def mark_favorite(label: str, favorited: bool, expired: bool = False) -> str:
    if expired:
        return f"[COLOR {EXPIRED_COLOUR}]{label}[/COLOR]"
    return f"[COLOR {FAVORITE_COLOUR}]{label}[/COLOR]" if favorited else label


def favorite_context(kind: str, item_id: Any, season: Any = None,
                     payload: dict[str, Any] | None = None) -> list[tuple[str, str]]:
    if is_favorite(kind, item_id, season):
        return [(f"[B]{tr('fav_remove')}[/B]",
                 f"RunPlugin({plugin_url(mode='fav_remove', key=favorite_key(kind, item_id, season))})")]
    params = {"mode": "fav_add", "kind": kind, "id": item_id}
    if season is not None:
        params["season"] = season
    if payload:
        params["payload"] = encode_data(payload)
    return [(f"[B]{tr('fav_add')}[/B]", f"RunPlugin({plugin_url(**params)})")]

CONTENT_TYPES = {"movie": "movies", "tvshow": "tvshows", "season": "seasons",
                 "episode": "episodes"}

CONTENT_PRIORITY = ("movies", "tvshows", "seasons", "episodes", "videos")

_content_counts: dict[str, int] = {}
_declared_content: dict[str, Any] = {}


def declare_content(kind: str) -> None:
    _content_counts[kind] = _content_counts.get(kind, 0) + 1
    best = max(_content_counts.items(),
               key=lambda item: (item[1], -CONTENT_PRIORITY.index(item[0])
                                 if item[0] in CONTENT_PRIORITY else -len(CONTENT_PRIORITY)))[0]
    if best == _declared_content.get("value"):
        return
    _declared_content["value"] = best
    try:
        xbmcplugin.setContent(HANDLE, best)
        if not _declared_content.get("sorted"):
            xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_UNSORTED)
            _declared_content["sorted"] = True
    except Exception as exc:
        log(f"Could not declare content type {best}: {exc}", xbmc.LOGWARNING)

CACHE_TO_DISC = False


def set_category(title: str = "") -> None:
    xbmcplugin.setPluginCategory(HANDLE, f"{ADDON_NAME} - {title}" if title else ADDON_NAME)


def display_title(label: str, info: dict[str, Any] | None) -> str:
    if info is not None:
        info["title"] = label
    return label


def add_directory(title: str, params: dict[str, Any], art: str = "", plot: str = "",
                  context: list[tuple[str, str]] | None = None,
                  info: dict[str, Any] | None = None) -> None:
    item = xbmcgui.ListItem(label=title)
    if info:
        apply_video_info(item, info)
    elif plot:
        apply_video_info(item, {"title": title, "plot": plot})
    if art:
        item.setArt({"thumb": art, "icon": art, "poster": art, "fanart": art})
    if context:
        item.addContextMenuItems(context)
    xbmcplugin.addDirectoryItem(HANDLE, plugin_url(**params), item, True)


def add_next_page(params: dict[str, Any]) -> None:
    add_directory(f"[B][COLOR {PAGING_COLOUR}]{tr('next_page')}[/COLOR][/B]", params)


def artwork(asset: dict[str, Any], parent: dict[str, Any] | None = None) -> dict[str, str]:
    images = asset.get("images")
    poster = first_image(images, ("VOD_POSTER_2_3", "VOD_POSTER_21_31"))
    landscape = first_image(images, ("EVENT_16_9", "BACKDROP_16_9", "STB_XL"))
    if parent:
        parent_images = parent.get("images")
        poster = poster or first_image(parent_images, ("VOD_POSTER_2_3", "VOD_POSTER_21_31"))
        landscape = landscape or first_image(parent_images, ("EVENT_16_9", "BACKDROP_16_9", "STB_XL"))
    episode = asset.get("episodeNumber") is not None
    thumb = (landscape or poster) if episode else (poster or landscape)
    art = {}
    for role, value in (("thumb", thumb), ("icon", thumb),
                        ("poster", poster or thumb), ("fanart", landscape or poster)):
        if value:
            art[role] = value
    return art


def people_by_role(asset: dict[str, Any], role: str) -> list[str]:
    out = []

    def take(person: dict[str, Any]) -> None:
        name = " ".join(part for part in (person.get("firstName"), person.get("lastName")) if part).strip()
        if name and name not in out:
            out.append(name)

    for person in asset.get("people") or []:
        if ((person.get("occupation") or {}).get("identifier") or "") == role:
            take(person)
    for group in asset.get("castAndCrew") or []:
        if (group or {}).get("occupation") != role:
            continue
        for person in group.get("people") or []:
            take(person)
    return out


def same_title(left: str, right: str) -> bool:
    articles = ("the ", "a ", "an ")

    def norm(value: str) -> str:
        cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in str(value))
        cleaned = " ".join(cleaned.split()).casefold()
        for article in articles:
            if cleaned.startswith(article):
                cleaned = cleaned[len(article):]
                break
        return cleaned

    return norm(left) == norm(right)


def format_expiry(asset: dict[str, Any]) -> str:
    raw = asset.get("expirationDate")
    try:
        stamp = int(raw) / 1000
    except (TypeError, ValueError):
        return ""
    if stamp <= 0:
        return ""
    try:
        return time.strftime("%d %b %Y", time.localtime(stamp))
    except (ValueError, OSError):
        return ""


def runtime_seconds(asset: dict[str, Any]) -> int:
    try:
        return int(int(asset.get("duration") or 0) / 1000)
    except (TypeError, ValueError):
        return 0


def format_runtime(seconds: int) -> str:
    minutes = int(seconds or 0) // 60
    return f"{minutes} min" if minutes > 0 else ""


def format_quality(asset: dict[str, Any]) -> str:
    quality = str(asset.get("mediaQuality") or "").strip()
    return quality.replace("_", "/") if quality else ""


def asset_genres(asset: dict[str, Any]) -> list[str]:
    reserved = section_label_names()
    genres = [name for name in membership_names(asset, "category")
              if " ".join(name.split()).casefold() not in reserved]
    return genres or list(asset.get("adGenres") or [])


def premiere_date(asset: dict[str, Any], year: int) -> str:
    try:
        stamp = int(asset.get("premiereDate")) / 1000
    except (TypeError, ValueError):
        stamp = 0
    if stamp > 0:
        try:
            return time.strftime("%Y-%m-%d", time.localtime(stamp))
        except (ValueError, OSError):
            pass
    return f"{int(year):04d}-01-01" if year else ""


def asset_metadata(asset: dict[str, Any], media_type: str = "") -> dict[str, Any]:
    description = (asset.get("longDescription") or asset.get("shortDescription") or "").strip()
    year = asset.get("year") or asset.get("firstYear") or 0
    certificate = f"PG-{age_rating(asset)}" if age_rating(asset) else ""
    genres = asset_genres(asset)

    original = (asset.get("originalTitle") or "").strip()
    plot = description
    if original and not same_title(original, item_title(asset)):
        plot = f"[I]{original}[/I]" + ("\n\n" + description if description else "")

    expiry = format_expiry(asset)
    kind = media_type or ("tvshow" if is_series(asset) else (
        "episode" if asset.get("episodeNumber") is not None else "movie"))
    trailer = " • ".join(part for part in (
        format_quality(asset),
        format_runtime(runtime_seconds(asset)),
        f"{tr('available_until')} {expiry}" if expiry else "",
    ) if part)
    if trailer:
        plot = (plot + "\n\n" if plot else "") + f"[COLOR {MUTED_COLOUR}]{trailer}[/COLOR]"

    info: dict[str, Any] = {
        "title": item_title(asset),
        "plot": plot,

        "plotoutline": description,
        "year": year,

        "premiered": premiere_date(asset, year),
        "duration": runtime_seconds(asset),

        "mediatype": kind,
        "genre": genres,

        "tagline": ", ".join(genres) if not is_series(asset)
                   and asset.get("episodeNumber") is None else "",
        "studio": network_names(asset),
        "originaltitle": asset.get("originalTitle") or "",
        "country": [asset.get("country")] if asset.get("country") else [],
        "cast": people_by_role(asset, "ACTOR") + people_by_role(asset, "HOST"),

        "director": people_by_role(asset, "DIRECTOR"),
        "rating": asset_rating(asset),

        "mpaa": certificate,
    }
    position, total = resume_point(asset.get("id"))
    provider_watched, provider_position = provider_progress(asset)
    if position <= 0 and provider_position > 0:
        position, total = provider_position, float(runtime_seconds(asset))
    if position > 0:
        info["resume_position"] = position
        info["resume_total"] = total

    if is_series(asset):
        played = 1 if series_watched(asset) else 0
    else:
        played = watch_count(asset.get("id")) or provider_watched
    if played:
        info["playcount"] = played

    if asset.get("seriesTitle"):
        info["tvshowtitle"] = asset["seriesTitle"]
    if asset.get("seasonNumber") is not None:
        info["season"] = asset["seasonNumber"]
    if asset.get("episodeNumber") is not None:
        info["episode"] = asset["episodeNumber"]
    return info


def episodes_year(episodes: list[dict[str, Any]] | None) -> int:
    years = []
    for episode in episodes or []:
        if not isinstance(episode, dict):
            continue
        year = episode.get("year") or episode.get("firstYear") or 0
        if not year:
            try:
                stamp = int(episode.get("premiereDate")) / 1000
            except (TypeError, ValueError):
                stamp = 0
            if stamp > 0:
                try:
                    year = int(time.strftime("%Y", time.localtime(stamp)))
                except (ValueError, OSError):
                    year = 0
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = 0
        if year > 0:
            years.append(year)
    return min(years) if years else 0


def season_word() -> str:
    return xbmc.getLocalizedString(20373) or "Season"


def episode_word() -> str:
    return xbmc.getLocalizedString(20359) or "Episode"


def season_metadata(series: dict[str, Any], season: dict[str, Any],
                    label: str = "") -> dict[str, Any]:
    merged = dict(series)
    merged.update({key: value for key, value in season.items()
                   if value not in (None, "", []) and key != "episodes"})

    for field in ("longDescription", "shortDescription"):
        merged[field] = season.get(field) or ""

    merged["originalTitle"] = ""

    episode_year = episodes_year(season.get("episodes"))
    if episode_year:
        merged["year"] = episode_year
        merged["firstYear"] = episode_year
        merged["premiereDate"] = None
    info = asset_metadata(merged, media_type="season")

    if label:
        info["title"] = label
    if season.get("seasonNumber") is not None:
        info["season"] = season["seasonNumber"]
    if series.get("title"):
        info["tvshowtitle"] = series["title"]
    return info


def set_stream_duration(item: xbmcgui.ListItem, tag: Any, seconds: Any) -> None:
    try:
        duration = int(seconds or 0)
    except (TypeError, ValueError):
        return
    if duration <= 0:
        return
    if tag is not None:
        try:
            tag.addVideoStream(xbmc.VideoStreamDetail(duration=duration))
            return
        except (AttributeError, TypeError, ValueError) as exc:
            log(f"Could not add video stream detail: {exc}", xbmc.LOGDEBUG)
    try:
        item.addStreamInfo("video", {"duration": duration})
    except (AttributeError, TypeError, ValueError):
        pass


def kodi_major() -> int:
    try:
        return int(xbmc.getInfoLabel("System.BuildVersion").split(".")[0])
    except (ValueError, AttributeError, IndexError):
        return 0


def apply_video_info(item: xbmcgui.ListItem, info: dict[str, Any]) -> None:
    tag = None
    try:
        tag = item.getVideoInfoTag()
    except AttributeError:
        tag = None

    if tag is None:
        item.setInfo("video", {k: v for k, v in info.items() if v not in (None, "", [], 0)})
        set_stream_duration(item, None, info.get("duration"))
        return

    def apply(setter_name: str, value: Any, cast=None) -> None:
        if value in (None, "", [], 0):
            return
        setter = getattr(tag, setter_name, None)
        if setter is None:
            return
        try:
            setter(cast(value) if cast else value)
        except (TypeError, ValueError) as exc:
            log(f"Could not set {setter_name}: {exc}", xbmc.LOGDEBUG)

    apply("setTitle", info.get("title"), str)
    apply("setPlot", info.get("plot"), str)
    apply("setPlotOutline", info.get("plotoutline"), str)
    apply("setTagLine", info.get("tagline"), str)
    apply("setMediaType", info.get("mediatype"), str)
    apply("setYear", info.get("year"), int)
    apply("setPremiered", info.get("premiered"), str)
    if info.get("mediatype") in ("episode", "season"):
        apply("setFirstAired", info.get("premiered"), str)
    apply("setDuration", info.get("duration"), int)
    set_stream_duration(item, tag, info.get("duration"))
    apply("setGenres", info.get("genre"), lambda v: [str(x) for x in v])
    apply("setStudios", info.get("studio"), lambda v: [str(x) for x in v])
    apply("setOriginalTitle", info.get("originaltitle"), str)
    apply("setCountries", info.get("country"), lambda v: [str(x) for x in v])
    apply("setDirectors", info.get("director"), lambda v: [str(x) for x in v])
    apply("setWriters", info.get("writer"), lambda v: [str(x) for x in v])
    apply("setMpaa", info.get("mpaa"), str)
    apply("setRating", info.get("rating"), float)
    apply("setTvShowTitle", info.get("tvshowtitle"), str)
    apply("setPremiered", info.get("premiered"), str)

    for key, setter_name in (("season", "setSeason"), ("episode", "setEpisode")):
        if info.get(key) is not None:
            setter = getattr(tag, setter_name, None)
            if setter is not None:
                try:
                    setter(int(info[key]))
                except (TypeError, ValueError):
                    pass

    apply("setPlaycount", info.get("playcount"), int)

    if info.get("resume_position"):
        try:
            tag.setResumePoint(float(info["resume_position"]), float(info.get("resume_total") or 0))
        except (AttributeError, TypeError, ValueError):
            pass

    if info.get("cast"):
        try:
            tag.setCast([xbmc.Actor(str(name), order=index)
                         for index, name in enumerate(info["cast"])])
        except (AttributeError, TypeError) as exc:
            log(f"Could not set cast: {exc}", xbmc.LOGDEBUG)


def add_action(title: str, params: dict[str, Any], art: str = "") -> None:
    item = xbmcgui.ListItem(label=title)
    if art:
        item.setArt({"thumb": art, "icon": art})
    xbmcplugin.addDirectoryItem(HANDLE, plugin_url(**params), item, False)


def publishing_points(asset: dict[str, Any]) -> list[dict[str, Any]]:
    points = asset.get("publishingPoint") or []
    return points if isinstance(points, list) else []

DETAIL_WORKERS = 6

DETAIL_WAIT_TIMEOUT = 40


class DetailPrefetch:
    def __init__(self, api: "EonApi", ids: list[str], workers: int = DETAIL_WORKERS) -> None:
        self.api = api
        self.queue = list(ids)
        self.workers = workers
        self.results: dict[str, tuple[Any, Exception | None]] = {}
        self.pending: dict[str, threading.Event] = {}
        self.lock = threading.Lock()

        self.inflight = 0
        self.fill()

    def fill(self) -> None:
        started = 0
        while started < self.workers:
            with self.lock:
                if not self.queue or self.inflight >= self.workers:
                    return
                asset_id = self.queue.pop(0)
                event = threading.Event()
                self.pending[asset_id] = event
                self.inflight += 1
            thread = threading.Thread(target=self.fetch, args=(asset_id, event))

            thread.daemon = True
            thread.start()
            started += 1

    def fetch(self, asset_id: str, event: threading.Event) -> None:
        outcome: tuple[Any, Exception | None] = (None, None)
        try:
            outcome = (self.api.get_json(f"v1/vodassets/{asset_id}"), None)
        except BaseException as err:
            outcome = (None, err if isinstance(err, Exception) else RuntimeError(str(err)))
        finally:
            with self.lock:
                self.results[asset_id] = outcome
                self.inflight -= 1
            event.set()
            if outcome[1] is None:
                self.fill()

    def take(self, asset_id: str) -> Any:
        with self.lock:
            event = self.pending.get(asset_id)
        if event is None:
            return self.api.get_json(f"v1/vodassets/{asset_id}")

        if not event.wait(DETAIL_WAIT_TIMEOUT):
            with self.lock:
                self.pending.pop(asset_id, None)
            raise TimeoutError(f"Detail request for {asset_id} never came back")
        with self.lock:
            data, err = self.results.pop(asset_id, (None, None))
            self.pending.pop(asset_id, None)

        if err is not None:
            raise err
        return data

    def stop(self) -> None:
        with self.lock:
            self.queue = []


def asset_detail(api: EonApi, asset: dict[str, Any]) -> dict[str, Any]:
    asset_id = asset.get("id")
    if not asset_id:
        return asset
    cache_key = str(asset_id)
    if cache_key in api._asset_details:
        return api._asset_details[cache_key]
    try:
        detail = api.vod_detail(asset_id)
        api._asset_details[cache_key] = detail or asset
        return api._asset_details[cache_key]
    except Exception as exc:
        log(f"Failed to load VOD detail {asset_id}: {exc}", xbmc.LOGWARNING)
        return asset


def warm_details(api: EonApi, assets: list[dict[str, Any]]) -> None:
    ids = []
    for asset in assets:
        asset_id = asset.get("id")
        if not asset_id or is_series(asset):
            continue
        key = str(asset_id)
        if key not in api._asset_details and key not in ids:
            ids.append(key)

    if len(ids) < 2:
        return
    prefetch = DetailPrefetch(api, ids)
    try:
        for key in ids:
            try:
                detail = prefetch.take(key)
            except Exception as exc:
                log(f"Detail prefetch failed for {key}: {exc}", xbmc.LOGDEBUG)
                continue
            if detail:
                api._asset_details[key] = detail
    finally:
        prefetch.stop()

EPISODE_INHERITS = ("duration", "adGenres", "memberships", "sections", "categoryIds",
                    "ageRating", "mediaQuality", "country", "year", "firstYear",
                    "people", "castAndCrew", "assetRatings")


def with_series_context(episode: dict[str, Any], series: dict[str, Any] | None) -> dict[str, Any]:
    if not series:
        return episode
    filled = dict(episode)
    for field in EPISODE_INHERITS:
        if filled.get(field) in (None, "", [], 0) and series.get(field) not in (None, "", [], 0):
            filled[field] = series[field]

    if not filled.get("seriesTitle"):
        filled["seriesTitle"] = series.get("title") or series.get("seriesTitle")
    return filled


def episode_label(episode: dict[str, Any], series: dict[str, Any] | None,
                  season_number: Any = None, position: int = 0) -> str:
    if str(episode.get("episodeTitle") or "").strip():
        return item_title(episode)
    own = item_title(episode)
    show = item_title(series) if series else str(episode.get("seriesTitle") or "").strip()
    if not show or own.casefold() != show.casefold():
        return own
    number = episode.get("episodeNumber") or position
    season = season_number if season_number not in (None, "") else episode.get("seasonNumber")
    if not number or season in (None, ""):
        return own
    return f"{show} - S{season}:E{number}"


def add_asset(api: EonApi, asset: dict[str, Any], series: dict[str, Any] | None = None,
              season_number: Any = None, position: int = 0) -> None:
    if should_hide(asset):
        return

    if is_series(asset):
        declare_content("tvshows")
        title = item_title(asset)
        art = artwork(asset).get("thumb", "")
        plot = asset.get("longDescription") or asset.get("shortDescription") or ""
        series_info = asset_metadata(asset)

        add_directory(
            display_title(mark_favorite(f"[B]{title}[/B]",
                                        is_favorite("series", asset.get("id")),
                                        is_expired(asset)), series_info),
            {"mode": "asset", "id": asset.get("id")}, art, plot,
            favorite_context("series", asset.get("id"), payload=favorite_snapshot(asset, "series")),
            series_info,
        )
        return

    detail = asset_detail(api, asset)
    if not publishing_points(detail):
        log(f"Skipping non-playable VOD asset={asset.get('id')} title={item_title(asset)}",
            xbmc.LOGDEBUG)
        return

    detail = with_series_context(detail, series)

    declare_content("episodes" if detail.get("episodeNumber") is not None else "movies")
    title = episode_label(detail, series, season_number, position)
    log(f"Episode row {detail.get('id')}: title={detail.get('title')!r} "
        f"episodeTitle={detail.get('episodeTitle')!r} "
        f"episodeNumber={detail.get('episodeNumber')!r} "
        f"seasonNumber={detail.get('seasonNumber')!r} -> {title!r}", xbmc.LOGDEBUG)

    art_source = detail if detail.get("images") else asset
    art_roles = artwork(art_source, series)
    art = art_roles.get("thumb", "")
    plot = detail.get("longDescription") or detail.get("shortDescription") or asset.get("shortDescription") or ""

    favorited = is_favorite("asset", detail.get("id") or asset.get("id"))
    list_item = xbmcgui.ListItem(label=mark_favorite(title, favorited, is_expired(detail)))
    list_item.addContextMenuItems(
        favorite_context("asset", detail.get("id") or asset.get("id"),
                         payload=favorite_snapshot(detail, "asset"))
    )

    info = asset_metadata(detail)

    info["title"] = title
    apply_video_info(list_item, info)
    list_item.setProperty("IsPlayable", "true")
    if art_roles:
        list_item.setArt(art_roles)
    xbmcplugin.addDirectoryItem(HANDLE, plugin_url(mode="play", id=detail.get("id") or asset.get("id")), list_item, False)

MAX_AGE_RATING = 18

UNRATED = -1

KIDS_CATEGORY_ID = 203


def max_age_rating() -> int:
    try:
        value = int(ADDON.getSetting("max_age_rating") or MAX_AGE_RATING)
    except (TypeError, ValueError):
        return MAX_AGE_RATING
    return max(0, min(MAX_AGE_RATING, value))


def age_rating(asset: dict[str, Any]) -> int:
    try:
        return int(asset.get("ageRating") or 0)
    except (TypeError, ValueError):
        return 0


def cached_asset(asset_id: str) -> dict[str, Any]:
    if not asset_id:
        return {}
    cache = load_cache()
    for asset in (cache or {}).get("assets") or []:
        if str(asset.get("id")) == str(asset_id):
            return asset
    return {}


def cached_sections(asset_id: str) -> list[str]:
    return cached_asset(asset_id).get("sections") or []


def full_asset(api: EonApi, asset_id: str) -> dict[str, Any]:
    try:
        detail = api.vod_detail(asset_id) or {}
    except Exception as exc:
        log(f"Detail unavailable for {asset_id}: {exc}", xbmc.LOGWARNING)
        detail = {}
    merged = dict(cached_asset(str(asset_id)))
    merged.update({key: value for key, value in detail.items() if value not in (None, "", [])})
    return merged or detail


def is_kids_title(asset: dict[str, Any], asset_id: str = "") -> bool:
    ids = [int(c) for c in (asset.get("categoryIds") or []) if str(c).isdigit()]
    if KIDS_CATEGORY_ID in ids:
        return True
    if "kids" in (asset.get("sections") or []):
        return True
    return "kids" in cached_sections(str(asset.get("id") or asset_id or ""))


def age_blocked(asset: dict[str, Any], asset_id: str = "") -> int:
    limit = max_age_rating()
    rating = age_rating(asset)
    if rating:
        return rating if rating > limit else 0
    if limit >= MAX_AGE_RATING:
        return 0
    return 0 if is_kids_title(asset, asset_id) else UNRATED

_hide_unsubscribed_memo: bool | None = None


def hide_unsubscribed() -> bool:
    global _hide_unsubscribed_memo
    if _hide_unsubscribed_memo is None:
        _hide_unsubscribed_memo = as_bool(ADDON.getSetting("hideunsubscribed"), True)
    return _hide_unsubscribed_memo


def should_hide(asset: dict[str, Any]) -> bool:
    if hide_unsubscribed() and asset.get("subscribed") is False:
        return True
    if asset.get("drmRequired") is True:
        return True
    return False

_cache_memo: Any = "__unread__"


def load_cache() -> dict[str, Any] | None:
    global _cache_memo
    if _cache_memo != "__unread__":
        return _cache_memo
    _cache_memo = None
    if not xbmcvfs.exists(CACHE_FILE):
        return None
    handle = None
    try:
        handle = xbmcvfs.File(CACHE_FILE, "r")
        cache = json.loads(handle.read())
        if cache.get("version") != CACHE_VERSION or cache.get("language") != metadata_language():
            return None
        _cache_memo = cache
        return cache
    except Exception as exc:
        log(f"Failed to read VOD cache: {exc}", xbmc.LOGWARNING)
        return None
    finally:
        if handle is not None:
            handle.close()


def save_cache(cache: dict[str, Any]) -> None:
    global _cache_memo
    folder = os.path.dirname(CACHE_FILE)
    if not xbmcvfs.exists(folder):
        xbmcvfs.mkdirs(folder)
    temporary = CACHE_FILE + ".part"
    handle = None
    try:
        handle = xbmcvfs.File(temporary, "w")
        handle.write(json.dumps(cache, ensure_ascii=False, separators=(",", ":")))
    except Exception:
        if handle is not None:
            handle.close()
            handle = None
        xbmcvfs.delete(temporary)
        raise
    finally:
        if handle is not None:
            handle.close()

    # Windows cannot rename over an existing file, and Kodi logs the failed
    # attempt as a loud XFILE ERROR before our fallback kicks in - so remove
    # the destination first there. POSIX replaces atomically; keep that.
    if xbmc.getCondVisibility("System.Platform.Windows") and xbmcvfs.exists(CACHE_FILE):
        xbmcvfs.delete(CACHE_FILE)
    if not xbmcvfs.rename(temporary, CACHE_FILE):
        if xbmcvfs.exists(CACHE_FILE):
            xbmcvfs.delete(CACHE_FILE)
        if not xbmcvfs.rename(temporary, CACHE_FILE):
            xbmcvfs.copy(temporary, CACHE_FILE)
            xbmcvfs.delete(temporary)

    _cache_memo = "__unread__"

    handle = None
    try:
        handle = xbmcvfs.File(SYNC_STATE_FILE, "w")
        handle.write(json.dumps({"version": cache.get("version"),
                                 "language": cache.get("language"),
                                 "synced_at": cache.get("synced_at")}))
    except Exception as exc:
        log(f"Could not write the sync state: {exc}", xbmc.LOGWARNING)
    finally:
        if handle is not None:
            handle.close()


def source_art(cache: dict[str, Any], name: str | None) -> str:
    if not name:
        return ""
    for source in cache.get("sources") or []:
        if source.get("name") == name:
            return source.get("art") or ""
    return ""


def source_art_by(cache: dict[str, Any], name: str | None, section: str | None = None, kind: str | None = None) -> str:
    if not name:
        return ""
    for source in cache.get("sources") or []:
        if source.get("name") != name:
            continue
        if section and source.get("section") != section:
            continue
        if kind and source.get("kind") != kind:
            continue
        return source.get("art") or ""
    return ""


def source_art_or_default(cache: dict[str, Any], name: str | None, fallback: str = "category") -> str:
    return source_art(cache, name) or media_icon(fallback)


def source_art_by_or_default(cache: dict[str, Any], name: str | None,
                             section: str | None = None, kind: str | None = None,
                             fallback: str = "category") -> str:
    return source_art_by(cache, name, section, kind) or source_art(cache, name) or media_icon(fallback)


def section_art_or_default(cache: dict[str, Any], section: str, fallback: str) -> str:
    return (cache.get("section_art") or {}).get(section) or media_icon(fallback)

SERIES_TYPES = ("SERIES", "REPLAY_SERIES")


def is_series(asset: dict[str, Any]) -> bool:
    return (asset.get("contentType") or asset.get("vodType")) in SERIES_TYPES


def cached_playable(asset: dict[str, Any]) -> bool:
    if is_series(asset):
        return True
    return bool(publishing_points(asset))


def source_kind(action: dict[str, Any]) -> str:
    if action.get("catalogueId"):
        return "network"
    if action.get("genreIds"):
        return "category"
    return "category"


def source_key(action: dict[str, Any], name: str, section: str) -> str:
    def part(value: Any) -> str:
        if isinstance(value, (list, tuple)):
            return ",".join(sorted(str(v) for v in value))
        return str(value or "")

    catalogue = part(action.get("catalogueId"))
    categories = part(action.get("categoryIds"))
    genres = part(action.get("genreIds"))
    if catalogue or categories or genres:
        return f"{section}:q:{catalogue}:{categories}:{genres}"
    return f"{section}:name:{name}"


def action_query(action: dict[str, Any]) -> dict[str, Any]:
    query = query_from_action(action, 0, 10000)
    query["size"] = 10000
    query["page"] = 0
    return query


def catalogue_sources(
    api: EonApi,
    item: dict[str, Any],
    section_key: str,
    depth: int = 0,
    parent_arts: list[str] | None = None,
) -> list[dict[str, Any]]:
    title = item_title(item)
    own_arts = catalogue_images(item.get("images"))

    arts = own_arts + [url for url in (parent_arts or []) if url not in own_arts]
    art = arts[0] if arts else ""
    actions = item.get("actions") or []
    action = actions[0] if actions else {}
    ref_type = action.get("refType")

    if ref_type == "VOD_ASSET":
        return [{"name": title, "art": art, "arts": arts, "action": action,
                 "section": section_key, "from_page": False}]

    if ref_type != "PAGE" or not action.get("pageId") or depth >= 4:
        return []

    target_page = str(action.get("pageId"))
    known_pages = set(SYNC_PAGES.values())
    for mapping in PORTAL_PAGES.values():
        known_pages.update(mapping.values())
    if target_page in known_pages:
        return []

    found: list[dict[str, Any]] = []
    try:
        stripes = page_stripes(api, str(action.get("pageId")))
    except Exception as exc:
        log(f"Nested catalogue load failed {title}: {exc}", xbmc.LOGWARNING)
        return found

    for stripe in stripes:
        if stripe.get("type") != "CATALOGUE":
            continue
        for child in stripe.get("items") or []:
            found.extend(catalogue_sources(api, child, section_key, depth + 1,
                                           own_arts or parent_arts))
    return found


def resolve_source_art(
    sources: dict[str, dict[str, Any]],
    candidates: dict[str, list[str]],
    generic: set[str],
) -> None:
    def same_thing(name: str | None) -> str:
        return " ".join((name or "").split()).casefold()

    names_by_art: dict[str, set[str]] = {}
    for source_id, urls in candidates.items():
        name = same_thing((sources.get(source_id) or {}).get("name"))
        for url in urls:
            names_by_art.setdefault(url, set()).add(name)
    shared = {url for url, names in names_by_art.items() if len(names) > 1}
    rejected = set(generic) | shared

    for source_id, source in sources.items():
        urls = candidates.get(source_id)
        if urls is None:
            urls = [source.get("art")] if source.get("art") else []
        source["art"] = next((url for url in urls if url not in rejected), "")

    art_by_catalogue: dict[str, str] = {}
    for source_id, source in sources.items():
        catalogue_id = str((source.get("action") or {}).get("catalogueId") or "")
        if catalogue_id and source.get("art"):
            if source_id == f"catalogue:{catalogue_id}" or catalogue_id not in art_by_catalogue:
                art_by_catalogue[catalogue_id] = source["art"]
    for source in sources.values():
        if source.get("art"):
            continue
        catalogue_id = str((source.get("action") or {}).get("catalogueId") or "")
        if catalogue_id:
            source["art"] = art_by_catalogue.get(catalogue_id, "")


def is_section_root_action(section_key: str, action: dict[str, Any]) -> bool:
    if action.get("catalogueId"):
        return False

    config = SECTIONS.get(section_key, {})
    categories = {str(value) for value in action.get("categoryIds") or []}
    genres = {str(value) for value in action.get("genreIds") or []}

    expected_category = str(config.get("category") or "")
    expected_genre = str(config.get("genre") or "")

    if expected_category and expected_category in categories and not genres:
        return True

    if expected_genre and expected_genre in genres and not categories:
        return True
    return False


class SyncProgress:
    def __init__(self, background: bool = False) -> None:
        self.background = background
        self.dialog = xbmcgui.DialogProgressBG() if background else xbmcgui.DialogProgress()

    GAP = "[CR]"

    def create(self, heading: str, message: str = "") -> None:
        self.heading = heading
        self.percent = 0
        if self.background:
            self.dialog.create(heading, message)
        else:
            self.dialog.create(heading, self.GAP + message)

    def update(self, percent: int, message: str = "") -> None:
        percent = max(self.percent, min(100, int(percent)))
        self.percent = percent
        if self.background:
            self.dialog.update(percent, self.heading, message)
        else:
            self.dialog.update(percent, self.GAP + message)

    def iscanceled(self) -> bool:
        return False if self.background else self.dialog.iscanceled()

    def close(self) -> None:
        try:
            self.dialog.close()
        except Exception:
            pass


def sync_cache(api: EonApi, interactive: bool = True, full_refresh: bool = False,
               background: bool = False) -> dict[str, Any]:
    global _cache_memo
    started = time.time()
    assets: dict[str, dict[str, Any]] = {}
    sources: dict[str, dict[str, Any]] = {}
    source_order: dict[str, int] = {}
    section_art: dict[str, str] = {}

    source_arts: dict[str, list[str]] = {}

    generic_art: set[str] = set()

    page_titles: dict[str, str] = {}
    progress = SyncProgress(background)
    if interactive:
        progress.create(ADDON_NAME, tr("syncing"))

    pages = portal_pages(getattr(api, "cdn_identifier", ""))
    sync_items = list(pages.items())
    main_sections = [key for key in pages if not SECTIONS.get(key, {}).get("parent")]
    main_total = max(1, len(main_sections))
    for page_index, (section_key, page_id) in enumerate(sync_items):
        section_percent = int(page_index * 20 / len(sync_items))
        if interactive:
            title = SECTIONS.get(section_key, {}).get("title") or section_key
            if section_key in main_sections:
                step = main_sections.index(section_key) + 1
                progress.update(section_percent,
                                f"{tr('loading_page')} {step}/{main_total} - {title}")
            else:
                progress.update(section_percent, f"{tr('loading')} {title}")
        for stripe_index, stripe in enumerate(page_stripes(api, page_id, page_titles)):
            stripe_type = stripe.get("type")

            if stripe_type == "VOD":
                stripe_name = item_title(stripe) or stripe.get("title") or ""
                stripe_items = stripe.get("items") or []
                if not stripe_name:
                    continue

                stripe_actions = stripe.get("actions") or []
                stripe_action = stripe_actions[0] if stripe_actions else {}
                if stripe_action.get("catalogueId") or stripe_action.get("categoryIds") or stripe_action.get("genreIds"):
                    try:
                        full = api.get_json("v1/vodassets", action_query(stripe_action))
                        stripe_items = full.get("content") or stripe_items
                    except Exception as exc:
                        log(f"Stripe {stripe_name} full fetch failed, using preview items: {exc}",
                            xbmc.LOGWARNING)

                if not stripe_items:
                    continue
                stripe_id = f"{section_key}:stripe:{stripe.get('id')}"
                source_arts.setdefault(stripe_id, list(catalogue_images(stripe.get("images"))))
                sources[stripe_id] = {
                    "name": stripe_name,
                    "action": stripe_action,
                    "art": catalogue_image(stripe.get("images")),

                    "kind": "stripe",
                    "section": section_key,

                    "order": stripe_index,
                }
                for item_index, asset in enumerate(stripe_items):
                    if should_hide(asset):
                        continue
                    asset_id = str(asset.get("id") or "")
                    if not asset_id:
                        continue
                    cached = assets.setdefault(asset_id, dict(asset))
                    cached.setdefault("memberships", [])
                    cached.setdefault("sections", [])
                    if section_key not in cached["sections"]:
                        cached["sections"].append(section_key)
                    if not any(m.get("key") == stripe_id for m in cached["memberships"]):
                        cached["memberships"].append(
                            {"name": stripe_name, "key": stripe_id, "kind": "stripe",
                             "section": section_key, "order": stripe_index,

                             "position": item_index}
                        )
                    cached.update({k: v for k, v in asset.items() if v not in (None, "", [])})
                continue

            if stripe_type != "CATALOGUE":
                continue

            if section_key == "home":
                continue

            for item in stripe.get("items") or []:
                if interactive and progress.iscanceled():
                    progress.close()
                    raise RuntimeError("VOD sync cancelled")

                for source in catalogue_sources(api, item, section_key):
                    action = source["action"]
                    source_name = source["name"]
                    source_id = source_key(action, source_name, section_key)
                    source_image = source["art"]

                    if is_section_root_action(section_key, action):
                        if source_image:
                            section_art.setdefault(section_key, source_image)

                        generic_art.update(source.get("arts") or ([source_image] if source_image else []))
                        continue
                    kind = source_kind(action)
                    if source_id not in sources:
                        source_order[source_id] = len(source_order)

                    arts = source_arts.setdefault(source_id, [])
                    for candidate in source.get("arts") or ([source_image] if source_image else []):
                        if candidate and candidate not in arts:
                            arts.append(candidate)
                    sources[source_id] = {"name": source_name, "action": action,
                                          "art": source_image,
                                          "kind": kind, "section": section_key,
                                          "order": source_order[source_id]}
                    try:
                        if interactive:
                            progress.update(section_percent, f"{tr('loading')} {source_name}")
                        data = api.get_json("v1/vodassets", action_query(action))
                    except Exception as exc:
                        log(f"VOD sync source failed {source_name}: {exc}", xbmc.LOGWARNING)
                        continue

                    for asset in data.get("content") or []:
                        if should_hide(asset):
                            continue
                        asset_id = str(asset.get("id") or "")
                        if not asset_id:
                            continue
                        cached = assets.setdefault(asset_id, dict(asset))
                        cached.setdefault("memberships", [])
                        cached.setdefault("sections", [])
                        if section_key not in cached["sections"]:
                            cached["sections"].append(section_key)
                        if not any(m.get("key") == source_id for m in cached["memberships"]):
                            cached["memberships"].append({"name": source_name, "key": source_id, "kind": kind,
                                                          "section": section_key,
                                                          "order": source_order[source_id]})
                        cached.update({k: v for k, v in asset.items() if v not in (None, "", [])})

    catalogues = api.catalogues()
    for cat_index, cat in enumerate(catalogues):
        if interactive and progress.iscanceled():
            progress.close()
            raise RuntimeError("VOD sync cancelled")
        catalogue_id = str(cat.get("id") or "")
        if not catalogue_id:
            continue
        catalogue_name = cat.get("title") or f"Catalogue {catalogue_id}"
        if interactive:
            progress.update(
                20 + int(cat_index * 5 / max(1, len(catalogues))),
                f"{tr('loading')} {catalogue_name}",
            )
        source_id = f"catalogue:{catalogue_id}"
        source_arts.setdefault(source_id, list(catalogue_images(cat.get("images"))))
        sources[source_id] = {
            "name": catalogue_name,
            "action": {"catalogueId": catalogue_id},
            "art": catalogue_image(cat.get("images")),
            "kind": "network",
            "section": None,
            "catalogue_id": catalogue_id,
        }
        try:
            data = api.get_json("v1/vodassets", action_query({"catalogueId": catalogue_id}))
        except Exception as exc:
            log(f"VOD sync catalogue failed {catalogue_name}: {exc}", xbmc.LOGWARNING)
            continue
        for asset in data.get("content") or []:
            if should_hide(asset):
                continue
            asset_id = str(asset.get("id") or "")
            if not asset_id:
                continue
            cached = assets.setdefault(asset_id, dict(asset))
            cached.setdefault("memberships", [])
            cached.setdefault("sections", [])
            if not any(m.get("key") == source_id for m in cached["memberships"]):
                cached["memberships"].append(
                    {"name": catalogue_name, "key": source_id, "kind": "network",
                     "section": None, "catalogue_id": catalogue_id}
                )
            cached.update({k: v for k, v in asset.items() if v not in (None, "", [])})

    prior: dict[str, dict[str, Any]] = {}
    if not full_refresh:
        previous = load_cache()
        if previous:
            for old in previous.get("assets") or []:
                old_id = str(old.get("id") or "")

                if old_id and (old.get("detail_synced") or publishing_points(old)):
                    prior[old_id] = old

    total = max(1, len(assets))
    reused = 0
    fetched = 0

    needed = [
        str(asset_id)
        for asset_id, asset in assets.items()
        if prior.get(str(asset_id)) is None
    ]
    prefetch = DetailPrefetch(api, needed) if needed else None

    for index, (asset_id, asset) in enumerate(list(assets.items())):
        if interactive and progress.iscanceled():
            if prefetch:
                prefetch.stop()
            progress.close()
            raise RuntimeError("VOD sync cancelled")
        if interactive and index % 20 == 0:
            progress.update(25 + int(index * 70 / total), f"{tr('checking')} {index + 1}/{total}")

        known = prior.get(str(asset_id))
        if known is not None:
            for key, value in known.items():
                if key in ("memberships", "sections"):
                    continue
                if value not in (None, "", []) and asset.get(key) in (None, "", []):
                    asset[key] = value
            asset["detail_synced"] = True
            reused += 1
            continue

        try:
            detail = prefetch.take(str(asset_id)) if prefetch else asset_detail(api, asset)
            detail = detail or asset
            asset.update({k: v for k, v in detail.items() if v not in (None, "", [])})
            asset["detail_synced"] = True
            fetched += 1
        except Exception as exc:
            log(f"VOD sync detail failed {asset_id}: {exc}", xbmc.LOGWARNING)

    if prefetch:
        prefetch.stop()

    log(f"VOD sync detail phase: {reused} reused from cache, {fetched} fetched")

    prior.clear()
    _cache_memo = "__unread__"

    assets = {asset_id: asset for asset_id, asset in assets.items() if cached_playable(asset)}

    main_sections = {key for key, config in SECTIONS.items() if not config.get("parent")}
    for asset in assets.values():
        if any(name in main_sections for name in asset.get("sections") or []):
            continue

        for category_id in asset.get("categoryIds") or []:
            section_key = SECTION_BY_CATEGORY.get(str(category_id))
            if section_key and section_key not in (asset.get("sections") or []):
                asset.setdefault("sections", []).append(section_key)
        if any(name in main_sections for name in asset.get("sections") or []):
            continue

        asset.setdefault("sections", []).append("series" if is_series(asset) else "movies")

    resolve_source_art(sources, source_arts, generic_art)

    section_titles = {key: page_titles[page] for key, page in pages.items()
                      if page_titles.get(page)}

    cache = {
        "version": CACHE_VERSION,
        "language": metadata_language(),
        "synced_at": int(time.time()),
        "sources": list(sources.values()),
        "section_art": section_art,
        "section_titles": section_titles,
        "assets": list(assets.values()),
    }

    if not assets:
        if interactive:
            progress.close()
        log("VOD sync produced NO titles - the existing cache is left untouched. Check the "
            "lines above for 'Failed to load page' and 'Could not fetch v1/catalogues', and "
            "for the resolved API host: a brand resolved to the wrong provider's host answers "
            "both of those the same way.", xbmc.LOGERROR)
        if interactive:
            notify(tr("sync_empty"), 8000)
        raise RuntimeError(tr("sync_empty"))

    if interactive:
        progress.update(100, tr("saving"))
    save_cache(cache)
    if interactive:
        progress.close()
    log(f"VOD sync finished assets={len(assets)} seconds={time.time() - started:.1f}")
    if interactive:
        notify(f"{tr('synced')} {len(assets)} {tr('items')}")
    return cache


def cached_assets(
    cache: dict[str, Any],
    content_type: str | None = None,
    membership: str | None = None,
    required_memberships: list[str] | None = None,
    section: str | None = None,
    membership_kind: str | None = None,
    counting: bool = False,
) -> list[dict[str, Any]]:
    result = []
    for asset in cache.get("assets") or []:
        if should_hide(asset):
            continue
        if not cached_playable(asset):
            continue

        if content_type:
            wanted = SERIES_TYPES if content_type == "SERIES" else (content_type,)
            if (asset.get("contentType") or asset.get("vodType")) not in wanted:
                continue
        if section and section not in (asset.get("sections") or []):
            continue

        if membership and not any(
            m.get("name") == membership and (not membership_kind or m.get("kind") == membership_kind)
            for m in asset.get("memberships") or []
        ):
            continue
        if required_memberships and not all(
                any(m.get("name") == required for m in asset.get("memberships") or [])
                for required in required_memberships):
            continue
        result.append(asset)

    if counting:
        return result
    if membership and result:
        positions = {}
        for asset in result:
            for m in asset.get("memberships") or []:
                if m.get("name") == membership and m.get("kind") == "stripe" and m.get("position") is not None:
                    positions[id(asset)] = int(m["position"])
                    break
        if len(positions) == len(result):
            return sorted(result, key=lambda a: positions[id(a)])

    return sort_assets(result)


def membership_names(asset: dict[str, Any], kind: str | None = None) -> list[str]:
    names = []
    for membership in asset.get("memberships") or []:
        if kind and membership.get("kind") != kind:
            continue
        name = membership.get("name")
        if name and name not in names:
            names.append(name)
    return names


def network_names(asset: dict[str, Any]) -> list[str]:
    names = []
    for membership in asset.get("memberships") or []:
        if membership.get("kind") != "network":
            continue
        if not (membership.get("catalogue_id")
                or str(membership.get("key") or "").startswith("catalogue:")):
            continue
        name = membership.get("name")
        if name and name not in names:
            names.append(name)
    return names


def add_cached_asset(asset: dict[str, Any], context_override: list[tuple[str, str]] | None = None,
                     section_hint: str = "", mark: bool = True) -> None:
    content_type = asset.get("contentType") or asset.get("vodType")
    title = item_title(asset)
    art_roles = artwork(asset)
    art = art_roles.get("thumb", "")
    if not art:
        log(f"No artwork for cached asset id={asset.get('id')} title={title} "
            f"images={len(asset.get('images') or [])}", xbmc.LOGDEBUG)
        art = media_icon("series" if content_type in SERIES_TYPES else "movies")
    info = asset_metadata(asset)
    declare_content(CONTENT_TYPES.get(info["mediatype"], "videos"))
    plot = info["plot"]
    label = title
    if section_hint:
        label += f"  [COLOR {MUTED_COLOUR}]({section_hint})[/COLOR]"
    kind = "series" if is_series(asset) else "asset"

    favorited = mark and is_favorite(kind, asset.get("id"))
    snapshot = favorite_snapshot(asset, kind)
    context = context_override or favorite_context(kind, asset.get("id"), payload=snapshot)

    if is_series(asset):
        display = display_title(mark_favorite(f"[B]{label}[/B]", favorited, is_expired(asset)), info)
        add_directory(display, {"mode": "asset", "id": asset.get("id")}, art, plot, context, info)
        return

    item = xbmcgui.ListItem(label=display_title(
        mark_favorite(label, favorited, is_expired(asset)), info))
    item.addContextMenuItems(context)
    apply_video_info(item, info)
    item.setProperty("IsPlayable", "true")
    item.setArt(art_roles or {"thumb": art, "icon": art})
    xbmcplugin.addDirectoryItem(HANDLE, plugin_url(mode="play", id=asset.get("id")), item, False)


def page_stripes(api: EonApi, page_id: str, titles: dict[str, str] | None = None) -> list[dict[str, Any]]:
    try:
        page = api.get_json(f"ps/v2/pages/{page_id}")
    except Exception as exc:
        log(f"Failed to load page {page_id}, skipping this section: {exc}", xbmc.LOGWARNING)
        return []

    if titles is not None and page.get("title"):
        titles[str(page_id)] = page["title"]
    stripes = page.get("stripes") or []
    missing = [
        stripe.get("id")
        for stripe in stripes
        if stripe.get("id") and stripe.get("type") in ("CATALOGUE", "VOD") and not stripe.get("items")
    ]
    for offset in range(0, len(missing), 4):
        try:
            loaded = api.get_json("ps/v2/stripes", {"id": ",".join(missing[offset : offset + 4])})
        except Exception as exc:
            log(f"Failed to load stripes batch {missing[offset:offset+4]} for page {page_id}: {exc}", xbmc.LOGWARNING)
            continue
        by_id = {stripe.get("id"): stripe for stripe in loaded or []}
        for index, stripe in enumerate(stripes):
            stripes[index] = by_id.get(stripe.get("id"), stripe)
    return stripes


def list_root(api: EonApi) -> None:
    problem = pvr_status(api)
    if problem:
        log(f"pvr.eon is not usable: {problem}", xbmc.LOGERROR)
        notify(problem, 6000)
        add_directory(problem, {"mode": "root"}, addon_icon())
        return

    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))

        add_directory(f"[B][COLOR {MENU_COLOUR_TOOLS}]{tr('tools')}[/COLOR][/B]",
                      {"mode": "tools"}, media_icon("tools"))
        return
    add_directory(
        f"[B][COLOR {MENU_COLOUR_FAVORITES}]{tr('favorites')}[/COLOR][/B]",
        {"mode": "favorites"},

        "DefaultFavourites.png",
        "",
        [(f"[B]{tr('fav_clear')}[/B]", f"RunPlugin({plugin_url(mode='fav_clear')})")],
    )
    add_directory(
        f"[B][COLOR {MENU_COLOUR_SEARCH}]{tr('search')}[/COLOR][/B]",
        {"mode": "search"},
        "DefaultAddonsSearch.png",
        "",
        [(f"[B]{tr('search_clear')}[/B]", f"RunPlugin({plugin_url(mode='search_clear')})")],
    )
    add_directory(tr("home"), {"mode": "group_networks", "section": "home"}, addon_icon())
    add_directory(tr("movies"), {"mode": "cache_type", "content_type": "MOVIE", "section": "movies"}, media_icon("movies"))
    add_directory(tr("series"), {"mode": "cache_type", "content_type": "SERIES", "section": "series"}, media_icon("series"))
    add_directory(tr("kids"), {"mode": "group_networks", "section": "kids"}, media_icon("kids"))
    add_directory(tr("documentaries"), {"mode": "group_networks", "section": "documentaries"}, media_icon("documentaries"))
    add_directory(tr("tvshows"), {"mode": "group_networks", "section": "tvshows"}, media_icon("tvshows"))
    add_directory(tr("tv_networks"), {"mode": "networks"}, media_icon("networks"))
    add_directory(f"[B][COLOR {MENU_COLOUR_TOOLS}]{tr('tools')}[/COLOR][/B]",
                  {"mode": "tools"}, media_icon("tools"))


def catalogue_art_from_assets(cache: dict[str, Any], catalogue_id: str) -> str:
    wanted = str(catalogue_id)
    for asset in cache.get("assets") or []:
        if wanted in {str(cid) for cid in (asset.get("catalogueIds") or [])}:
            art = first_image(
                asset.get("images"),
                ("VOD_POSTER_2_3", "VOD_POSTER_21_31", "EVENT_16_9", "STB_XL"),
            )
            if art:
                return art
    return ""


def list_networks(api: EonApi) -> None:
    set_category(tr("tv_networks"))

    catalogues = api.catalogues()
    if catalogues:
        cache = load_cache() or {}

        catalogues = sorted(catalogues, key=lambda cat: (cat.get("title") or "").casefold())
        for cat in catalogues:
            name = cat.get("title") or f"Catalogue {cat.get('id')}"

            art = (
                catalogue_image(cat.get("images"))
                or source_art(cache, name)
                or catalogue_art_from_assets(cache, str(cat.get("id")))
                or media_icon("networks")
            )
            add_directory(
                with_count(name, count) if (count := count_catalogue(cache, str(cat.get("id")))) else name,
                {"mode": "catalogue", "id": str(cat.get("id")), "page": 0},
                art,
            )
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    log("v1/catalogues returned nothing; falling back to catalogues found during sync",
        xbmc.LOGWARNING)
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return
    names = sorted(
        {
            source.get("name")
            for source in cache.get("sources") or []
            if source.get("kind") == "network" and source.get("name")
        }
    )
    for name in names:
        add_directory(name, {"mode": "cache_items", "membership": name, "page": 0}, source_art_or_default(cache, name))
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_cache_category(category_id: str, page: int = 0) -> None:
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    wanted = str(category_id)
    items = sort_assets([
        asset
        for asset in cache.get("assets") or []
        if not should_hide(asset)
        and cached_playable(asset)
        and wanted in {str(cid) for cid in (asset.get("categoryIds") or [])}
    ])
    size = page_size()
    start = page * size
    for asset in items[start : start + size]:
        add_cached_asset(asset)
    if start + size < len(items):
        add_next_page({"mode": "cache_category", "category": category_id, "page": page + 1})
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def in_catalogue(asset: dict[str, Any], catalogue_id: str) -> bool:
    wanted = str(catalogue_id)
    key = f"catalogue:{wanted}"
    for m in asset.get("memberships") or []:
        if m.get("key") == key or str(m.get("catalogue_id") or "") == wanted:
            return True
    return wanted in {str(cid) for cid in (asset.get("catalogueIds") or [])}


def catalogue_assets_cached(cache: dict[str, Any], catalogue_id: str,
                            category_id: str | None = None) -> list[dict[str, Any]]:
    out = []
    for asset in cache.get("assets") or []:
        if should_hide(asset) or not cached_playable(asset):
            continue
        if not in_catalogue(asset, catalogue_id):
            continue
        if category_id and str(category_id) not in {str(c) for c in (asset.get("categoryIds") or [])}:
            continue
        out.append(asset)
    return sort_assets(out)


def list_catalogue(api: EonApi, catalogue_id: str, page: int = 0) -> None:
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    items = catalogue_assets_cached(cache, catalogue_id)
    size = page_size()
    start = page * size
    for asset in items[start : start + size]:
        add_cached_asset(asset)
    if start + size < len(items):
        add_next_page({"mode": "catalogue", "id": catalogue_id, "page": page + 1})
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def section_shortcut_names(section: str | None = None) -> set[str]:
    names = {tr("tv_networks")}
    if section:
        cfg = SECTIONS.get(section, {})
        if cfg.get("title"):
            names.add(cfg["title"])
        if section in SECTION_LABEL_KEYS:
            names.add(tr(section))
    return {" ".join(n.split()).casefold() for n in names if n}


def section_network_names(cache: dict[str, Any], section: str, api: EonApi | None = None) -> list[str]:
    shortcuts = section_shortcut_names(section)

    def keep(name: str) -> bool:
        return " ".join(str(name).split()).casefold() not in shortcuts

    return [name for name in names_in_server_order(cache, section, "network") if keep(name)]


def with_count(name: str, count: int) -> str:
    return f"{name}  [COLOR {MUTED_COLOUR}]({count})[/COLOR]"


def count_membership(cache: dict[str, Any], name: str, section: str | None = None,
                     content_type: str | None = None, kind: str | None = None) -> int:
    return sum(1 for _ in cached_assets(cache, content_type, name, section=section,
                                        membership_kind=kind, counting=True))


def count_catalogue(cache: dict[str, Any], catalogue_id: str) -> int:
    return sum(
        1
        for asset in cache.get("assets") or []
        if not should_hide(asset) and cached_playable(asset) and in_catalogue(asset, catalogue_id)
    )


SORT_MODES = {
    "0": "DATE_ADDED",
    "1": "AZ",
    "2": "RATING",
    "3": "RELEASE_DATE_DESC",
    "4": "RELEASE_DATE_ASC",
}


def asset_rating(asset: dict[str, Any]) -> float:
    best = 0.0
    for entry in asset.get("assetRatings") or []:
        try:
            value = float(entry.get("rating"))
        except (TypeError, ValueError):
            continue
        if entry.get("metadataProviderName") == "Imdb":
            return value
        best = max(best, value)
    return best


def asset_year(asset: dict[str, Any]) -> int:
    for field in ("year", "firstYear"):
        try:
            value = int(asset.get(field) or 0)
        except (TypeError, ValueError):
            continue
        if value:
            return value
    return 0


def sort_assets(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        mode = SORT_MODES.get(str(ADDON.getSetting("sort_mode") or "0"), "DATE_ADDED")
    except Exception:
        mode = "DATE_ADDED"

    if mode == "DATE_ADDED":
        return sorted(items, key=lambda a: (-int(a.get("dateAdded") or 0), item_title(a).casefold()))
    if mode == "RATING":
        return sorted(items, key=lambda a: (asset_rating(a) <= 0, -asset_rating(a), item_title(a).casefold()))
    if mode == "RELEASE_DATE_DESC":
        return sorted(items, key=lambda a: (asset_year(a) == 0, -asset_year(a), item_title(a).casefold()))
    if mode == "RELEASE_DATE_ASC":
        return sorted(items, key=lambda a: (asset_year(a) == 0, asset_year(a), item_title(a).casefold()))
    return sorted(items, key=lambda a: item_title(a).casefold())


def names_in_server_order(cache: dict[str, Any], section: str | None, kind: str) -> list[str]:
    best: dict[str, tuple[int, str]] = {}
    for asset in cache.get("assets") or []:
        for m in asset.get("memberships") or []:
            if m.get("kind") != kind:
                continue
            if section is not None and m.get("section") != section:
                continue
            name = m.get("name")
            if not name:
                continue
            order = int(m.get("order") or 0)
            if name not in best or order < best[name][0]:
                best[name] = (order, name)
    return [name for _order, name in sorted(best.values())]


def stripe_names(cache: dict[str, Any], section: str | None,
                 exclude: set[str] | None = None) -> list[str]:
    def norm(value: str) -> str:
        return " ".join(str(value).split()).casefold()

    taken = {norm(name) for name in (exclude or ()) if name}
    taken.update(
        norm(m.get("name"))
        for asset in cache.get("assets") or []
        for m in asset.get("memberships") or []
        if m.get("kind") == "network" and m.get("name")
    )

    seen: dict[str, tuple[int, str]] = {}
    for asset in cache.get("assets") or []:
        for m in asset.get("memberships") or []:
            if m.get("kind") != "stripe":
                continue
            if section and m.get("section") != section:
                continue
            name = m.get("name")
            if not name or norm(name) in taken or norm(name) in seen:
                continue
            seen[norm(name)] = (int(m.get("order") or 0), name)

    return [name for _order, name in sorted(seen.values())]


def pvr_status(api: EonApi) -> str:
    if api.pvr_addon is None and not xbmcvfs.exists(
        xbmcvfs.translatePath(f"special://profile/addon_data/{PVR_ADDON_ID}/settings.xml")
    ):
        return tr("pvr_missing")
    if not api.settings.access_token and not api.settings.refresh_token:
        return tr("pvr_not_logged_in")
    if not api.settings.stream_key or not api.settings.stream_user:
        return tr("pvr_no_stream_key")
    return ""

SECTION_LABEL_KEYS = {
    "movies": "movies", "series": "series", "kids": "kids",
    "documentaries": "documentaries", "tvshows": "tvshows", "home": "home",
}


def section_title(section: str | None, cache: dict[str, Any] | None = None) -> str:
    if not section:
        return ""
    if cache is None:
        cache = load_cache()
    title = ((cache or {}).get("section_titles") or {}).get(section)
    return title or SECTIONS.get(section, {}).get("title") or section

_section_label_memo: set[str] | None = None


def section_label_names() -> set[str]:
    global _section_label_memo
    if _section_label_memo is None:
        names = {cfg.get("title") for cfg in SECTIONS.values() if cfg.get("title")}
        names.update(tr(label) for label in SECTION_LABEL_KEYS.values())
        _section_label_memo = {" ".join(str(name).split()).casefold() for name in names if name}
    return _section_label_memo


def section_labels(asset: dict[str, Any]) -> str:
    names = []
    for key in asset.get("sections") or []:
        label = tr(SECTION_LABEL_KEYS[key]) if key in SECTION_LABEL_KEYS else (
            SECTIONS.get(key, {}).get("title") or key
        )
        if label not in names:
            names.append(label)
    return ", ".join(names)


def search_haystack(asset: dict[str, Any]) -> str:
    parts = [
        asset.get("title") or "",
        asset.get("originalTitle") or "",
        asset.get("seriesTitle") or "",
    ]
    parts += people_by_role(asset, "ACTOR")
    parts += people_by_role(asset, "DIRECTOR")
    parts += people_by_role(asset, "HOST")
    return " \n ".join(parts).casefold()


def run_search(query: str) -> list[dict[str, Any]]:
    cache = load_cache()
    if not cache:
        return []
    assets = cache.get("assets") or []
    needle = " ".join(query.split()).casefold()
    if not needle:
        return []
    year_query = int(needle) if needle.isdigit() and len(needle) == 4 else 0

    hits: list[dict[str, Any]] = []
    for asset in assets:
        if should_hide(asset) or not cached_playable(asset):
            continue

        if year_query and asset_year(asset) == year_query:
            hits.append(asset)
            continue
        if needle in search_haystack(asset):
            hits.append(asset)

    def rank(asset: dict[str, Any]) -> tuple[int, str]:
        title = (asset.get("title") or "").casefold()
        if title.startswith(needle):
            return (0, title)
        if needle in title:
            return (1, title)

        return (2, title)

    return sorted(hits, key=rank)


def list_search_root() -> None:
    set_category(tr("search"))
    add_action(f"[B][COLOR {MENU_COLOUR_SEARCH}]{tr('search_new')}[/COLOR][/B]",
               {"mode": "search_new"}, "DefaultAddonsSearch.png")
    for query in load_searches():
        add_directory(
            query,
            {"mode": "search_do", "q": query},
            "DefaultAddonsSearch.png",
            "",
            [(f"[B]{tr('search_forget')}[/B]",
              f"RunPlugin({plugin_url(mode='search_forget', q=query)})")],
        )
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_search_results(api: EonApi, query: str) -> None:
    set_category(f"{tr('search')}: {query}")
    """Searching runs against the cache: no network, and it finishes before the screen
    redraws. EON's own v1/search was tried alongside it and returned the same titles, so it
    only added a request and a row to ignore."""
    results = run_search(query)
    if results:
        remember_search(query)
    if not results:
        add_directory(f"{tr('search_none')} \"{query}\"", {"mode": "search"}, addon_icon())
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return
    for asset in results:
        add_cached_asset(asset, section_hint=section_labels(asset))

    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_favorites() -> None:
    set_category(tr("favorites"))
    entries = load_favorites()
    if not entries:
        add_action(tr("fav_empty"), {"mode": "go_back"}, addon_icon())
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    for entry in entries:
        payload = entry.get("payload") or {}
        kind = entry.get("kind") or payload.get("kind") or "asset"
        key = entry.get("key")
        remove = [(f"[B]{tr('fav_remove')}[/B]",
                   f"RunPlugin({plugin_url(mode='fav_remove', key=key)})")]
        if kind == "season":
            title = payload.get("title") or tr("fav_season")
            add_directory(f"[B]{title}[/B]",
                          {"mode": "season", "series": payload.get("series"),
                           "season": payload.get("season")},
                          payload.get("art") or addon_icon(), "", remove)
        elif kind == "series":
            add_cached_asset(payload, context_override=remove, mark=False)
        else:
            add_cached_asset(payload, context_override=remove, mark=False)
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_stripes(section: str | None) -> None:
    set_category(section_title(section) or tr("categories"))
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return
    for name in stripe_names(cache, section):
        add_directory(
            with_count(name, count_membership(cache, name, section, kind="stripe")),
            {"mode": "cache_items", "membership": name, "section": section, "page": 0,
             "kind": "stripe"},
            source_art_by(cache, name, section, "stripe") or addon_icon(),
        )
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def child_sections(section: str, cache: dict[str, Any] | None = None) -> list[tuple[str, str]]:
    return sorted(
        ((key, section_title(key, cache)) for key, cfg in SECTIONS.items() if cfg.get("parent") == section),

        key=lambda pair: SECTIONS[pair[0]].get("page") or "",
    )


def list_group_networks(api: EonApi, section: str) -> None:
    set_category(section_title(section))
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    is_front_page = section == "home"
    names = [] if is_front_page else section_network_names(cache, section, api)
    children = child_sections(section, cache)

    shortcuts = section_shortcut_names(section)
    genres = [] if is_front_page else [
        n for n in names_in_server_order(cache, section, "category")
        if " ".join(n.split()).casefold() not in shortcuts
    ]

    stripes = stripe_names(cache, section, exclude=set(names))

    if not names and not stripes and not children and not genres:
        list_cache_items(None, None, section, 0)
        return

    add_directory(
        with_count("All", len(cached_assets(cache, None, section=section))),
        {"mode": "cache_items", "section": section, "page": 0},
        media_icon("category"),
    )

    if stripes:
        add_directory(tr("categories"), {"mode": "stripes", "section": section}, media_icon("category"))

    for name in genres:
        add_directory(
            with_count(name, count_membership(cache, name, section, kind="category")),
            {"mode": "cache_items", "membership": name, "section": section, "page": 0,
             "kind": "category"},
            source_art_by_or_default(cache, name, section, "category"),
        )

    for child_key, child_title in children:
        add_directory(
            with_count(child_title, len(cached_assets(cache, None, section=child_key))),
            {"mode": "group_networks", "section": child_key},
            section_art_or_default(cache, child_key, "category"),
        )

    for name in names:
        add_directory(
            with_count(name, count_membership(cache, name, section, kind="network")),
            {"mode": "cache_items", "membership": name, "section": section, "page": 0,
             "kind": "network"},
            source_art_by_or_default(cache, name, section, "network"),
        )
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def token_expiry_text(token: str) -> str:
    try:
        segment = token.split(".")[1]
        segment += "=" * (-len(segment) % 4)
        exp = int(json.loads(base64.urlsafe_b64decode(segment)).get("exp") or 0)
    except Exception:
        return tr("unknown")
    if not exp:
        return tr("unknown")
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(exp))
    return f"{when} ({tr('expired')})" if exp < time.time() else when


def show_cache_info() -> None:
    cache = load_cache()
    if not cache:
        xbmcgui.Dialog().ok(ADDON_NAME, tr("no_cache"))
        return
    assets = cache.get("assets") or []
    series = sum(1 for a in assets if is_series(a))
    synced = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(cache.get("synced_at") or 0)))

    sections = {}
    for asset in assets:
        for name in asset.get("sections") or []:
            if SECTIONS.get(name, {}).get("parent"):
                continue
            sections[name] = sections.get(name, 0) + 1
    lines = [
        "",
        f"{tr('cache_synced')}: {synced}",
        f"{tr('cache_titles')}: {len(assets)}  ({len(assets) - series} + {series} {tr('cache_series')})",
        f"{tr('cache_groupings')}: {len(cache.get('sources') or [])}",
        f"{tr('cache_language')}: {cache.get('language')}",
        f"{tr('cache_version')}: {cache.get('version')}",
        "",
    ]

    order = [key for key in SYNC_PAGES if not SECTIONS.get(key, {}).get("parent")]
    lines += [f"  {SECTIONS.get(name, {}).get('title') or name}: {sections[name]}"
              for name in order if name in sections]

    counted = sum(sections.get(name, 0) for name in order)
    placed = sum(1 for asset in assets
                 if any(name in order for name in asset.get("sections") or []))
    overlap = counted - placed
    unplaced = len(assets) - placed
    if overlap:
        lines.append(f"  {tr('cache_overlap')}: -{overlap}")
    if unplaced:
        lines.append(f"  {tr('cache_unplaced')}: {unplaced}")
    xbmcgui.Dialog().textviewer(ADDON_NAME, "\n".join(lines))


WIDEVINE_CDM_FILES = ("widevinecdm.dll", "libwidevinecdm.so", "libwidevinecdm.dylib")


def widevine_cdm_status() -> str:
    # Android ships Widevine as part of the OS (MediaDrm); everywhere else
    # inputstream.adaptive loads the CDM from special://home/cdm/.
    if xbmc.getCondVisibility("System.Platform.Android"):
        return tr("cdm_system")
    folder = xbmcvfs.translatePath("special://home/cdm/")
    if any(os.path.isfile(os.path.join(folder, name)) for name in WIDEVINE_CDM_FILES):
        return tr("cdm_installed")
    return tr("cdm_missing")


def widevine_ready() -> bool:
    # InputStream Helper checks inputstream.adaptive and the CDM, and offers to
    # install whatever is missing. Without it, fall back to looking for the CDM file.
    try:
        import inputstreamhelper
    except ImportError:
        log("script.module.inputstreamhelper is not available; checking the Widevine CDM "
            "file directly", xbmc.LOGWARNING)
        return widevine_cdm_status() != tr("cdm_missing")
    try:
        return bool(inputstreamhelper.Helper("hls", drm="com.widevine.alpha").check_inputstream())
    except Exception as exc:
        log(f"InputStream Helper check failed: {exc}", xbmc.LOGWARNING)
        return widevine_cdm_status() != tr("cdm_missing")


def show_account_info(api: EonApi) -> None:
    settings = api.settings
    lines = [
        "",
        f"{tr('acct_host')}: {API}",
        f"{tr('acct_provider')}: {api.service_provider_id() or tr('unknown')}",
        f"{tr('acct_device_id')}: {settings.device_id or tr('unknown')}",
        f"{tr('acct_device_number')}: {settings.device_number or tr('unknown')}",
        "",
        f"{tr('acct_access_token')}: {token_expiry_text(settings.access_token)}",
        f"{tr('acct_refresh_token')}: {token_expiry_text(settings.refresh_token)}",
        f"{tr('acct_widevine')}: {tr('yes') if api.widevine_url() else tr('no')} "
        f"({widevine_cdm_status()})",
    ]
    xbmcgui.Dialog().textviewer(ADDON_NAME, "\n".join(lines))


def cache_summary(cache: dict[str, Any] | None) -> str:
    if not cache:
        return tr("no_cache")
    assets = cache.get("assets") or []
    synced = time.strftime("%d.%m.%Y. %H:%M", time.localtime(int(cache.get("synced_at") or 0)))
    return f"{len(assets)} items, {synced}"


def account_summary(api: EonApi) -> str:
    try:
        segment = api.settings.refresh_token.split(".")[1]
        segment += "=" * (-len(segment) % 4)
        exp = int(json.loads(base64.urlsafe_b64decode(segment)).get("exp") or 0)
    except Exception:
        return tr("unknown")
    if not exp:
        return tr("unknown")
    when = time.strftime("%d.%m.%Y. %H:%M", time.localtime(exp))
    return f"{when} ({tr('expired')})" if exp < time.time() else when


def list_tools(api: EonApi) -> None:
    set_category(tr("tools"))
    cache = load_cache()

    add_action(f"[B][COLOR {MENU_COLOUR_TOOLS}]{tr('sync')}[/COLOR][/B]",
               {"mode": "sync"}, media_icon("tools"))
    add_action(tr("sync_full"), {"mode": "sync", "full": "1"}, media_icon("tools"))

    add_action(f"{tr('cache_info')}:  [COLOR {MUTED_COLOUR}]{cache_summary(cache)}[/COLOR]",
               {"mode": "cache_info"}, media_icon("tools"))
    add_action(f"{tr('account_info')}:  [COLOR {MUTED_COLOUR}]{account_summary(api)}[/COLOR]",
               {"mode": "account_info"}, media_icon("tools"))
    add_action(tr("cache_clear"), {"mode": "cache_clear"}, media_icon("tools"))
    add_action(f"{tr('fav_clear')}  [COLOR {MUTED_COLOUR}]({len(load_favorites())})[/COLOR]",
               {"mode": "fav_clear"}, media_icon("tools"))
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_cache_type(content_type: str, section: str | None) -> None:
    set_category(section_title(section))
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    names = names_in_server_order(cache, section, "category")

    add_directory(
        with_count("All", len(cached_assets(cache, content_type))),
        {"mode": "cache_items", "content_type": content_type, "page": 0},
        media_icon("category"),
    )

    stripes = stripe_names(cache, section)
    if stripes:
        add_directory(tr("categories"), {"mode": "stripes", "section": section}, media_icon("category"))
    for name in names:
        add_directory(
            with_count(name, count_membership(cache, name, section, content_type, kind="category")),
            {"mode": "cache_items", "content_type": content_type, "membership": name,
             "section": section, "page": 0, "kind": "category"},
            source_art_by_or_default(cache, name, section, "category"),
        )
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_cache_items(content_type: str | None, membership: str | None, section: str | None, page: int,
                     membership_kind: str | None = None) -> None:
    cache = load_cache()
    if not cache:
        add_action(tr("sync"), {"mode": "sync"}, media_icon("tools"))
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return
    items = cached_assets(cache, content_type, membership, section=section,
                          membership_kind=membership_kind)
    size = page_size()
    start = page * size
    for asset in items[start : start + size]:
        add_cached_asset(asset)
    if start + size < len(items):
        add_next_page({"mode": "cache_items", "content_type": content_type, "membership": membership, "section": section, "page": page + 1})
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def query_from_action(action: dict[str, Any], page: int, size: int) -> dict[str, Any]:
    query: dict[str, Any] = {
        "size": size,
        "page": page,
        "vodSort": "DATE_ADDED",
        "sortDir": "DESC",
    }
    if action.get("catalogueId"):
        query["catalogueId"] = action.get("catalogueId")
    if action.get("categoryIds"):
        query["categoryId"] = action.get("categoryIds")
    if action.get("genreIds"):
        query["genreId"] = action.get("genreIds")
    return query


def in_broadcast_order(items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    def key(item: dict[str, Any]) -> tuple[int, float, str]:
        raw = item.get(field)
        try:
            return (0, float(raw), "")
        except (TypeError, ValueError):
            return (1, 0.0, str(item.get("title") or "").casefold())
    return sorted(items, key=key)


def list_asset(api: EonApi, asset_id: str) -> None:
    asset = full_asset(api, asset_id)

    if not is_series(asset):
        add_asset(api, asset)
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return

    set_category(item_title(asset))
    seasons = api.get_json(f"v1/vodassets/{asset_id}/seasons")
    if len(seasons) == 1:
        episodes = in_broadcast_order(
            [ep for ep in seasons[0].get("episodes") or [] if not should_hide(ep)], "episodeNumber")
        warm_details(api, episodes)
        season_number = seasons[0].get("seasonNumber")
        for index, episode in enumerate(episodes, start=1):
            add_asset(api, episode, asset, season_number, index)
    else:
        for season in in_broadcast_order(seasons, "seasonNumber"):
            episodes = [episode for episode in season.get("episodes") or [] if not should_hide(episode)]
            if not episodes:
                continue

            season_title = (season.get("title") or "").strip()
            title = f"{season_word()} {season.get('seasonNumber')}"
            if season_title and not same_title(season_title, item_title(asset)):
                title = f"{title} - {season_title}"
            art_roles = artwork(season, asset)
            art = art_roles.get("thumb", "")

            season_no = season.get("seasonNumber")
            snapshot = {"title": title, "art": art, "series": asset_id, "season": season_no}
            season_info = season_metadata(asset, season, title)
            if season_watched(episodes):
                season_info["playcount"] = 1
            add_directory(
                display_title(mark_favorite(f"[B]{title}[/B]",
                                            is_favorite("season", asset_id, season_no)),
                              season_info),
                {"mode": "season", "series": asset_id, "season": season_no},
                art,
                "",
                favorite_context("season", asset_id, season_no, payload=snapshot),
                season_info,
            )
            declare_content("seasons")
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def list_season(api: EonApi, series_id: str, season_number: str) -> None:
    series = full_asset(api, series_id) or None
    if series:
        set_category(f"{item_title(series)} - {season_word()} {season_number}")
    seasons = api.get_json(f"v1/vodassets/{series_id}/seasons")
    for season in seasons:
        if str(season.get("seasonNumber")) == str(season_number):
            episodes = in_broadcast_order(
                [ep for ep in season.get("episodes") or [] if not should_hide(ep)], "episodeNumber")
            warm_details(api, episodes)
            for index, episode in enumerate(episodes, start=1):
                add_asset(api, episode, series, season_number, index)
            break
    xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)


def age_gate(api: EonApi, asset_id: str) -> int:
    try:
        asset = api.vod_detail(asset_id) or {}
    except Exception as exc:
        log(f"Age gate could not read asset {asset_id}: {exc}", xbmc.LOGWARNING)
        return 0

    if not age_rating(asset) and asset.get("seriesId"):
        try:
            series = api.vod_detail(asset["seriesId"]) or {}
        except Exception:
            series = {}
        if series:
            asset = series
    return age_blocked(asset, str(asset_id))


def play(api: EonApi, asset_id: str) -> None:
    blocked = age_gate(api, asset_id)
    if blocked:
        message = tr("age_unrated") if blocked == UNRATED else f"{tr('age_blocked')} PG-{blocked}"
        log(f"Playback refused by the age limit: asset={asset_id} rated "
            f"{'unrated' if blocked == UNRATED else 'PG-%d' % blocked}")
        notify(message, 6000)

        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    try:
        url, publishing_point = api.stream_url(asset_id)
        probe_sample = api.probe_stream_url(url)
    except Exception as exc:
        log(f"Playback failed: {exc}", xbmc.LOGERROR)
        set_resolved_failed(str(exc))
        return

    widevine = api.widevine_url()
    pre_auth = api.vod_pre_auth(publishing_point) if widevine else ""

    # An encrypted manifest (SAMPLE-AES session key) with no pre-auth token can
    # never play: inputstream.adaptive has nothing to decrypt with and dies on
    # "Cannot parse the manifest", which reads like a stream defect. Name the
    # real cause instead - the vod_pre_auth warning above this line carries the
    # server's HTTP code and response body.
    drm_manifest = "EXT-X-SESSION-KEY" in (probe_sample or "") \
        or "SAMPLE-AES" in (probe_sample or "")
    if drm_manifest and not pre_auth:
        log(f"Playback stopped for asset={asset_id}: the manifest is DRM protected "
            f"but EON issued no pre-auth token (see the warning above for the "
            f"server's reason)", xbmc.LOGERROR)
        set_resolved_failed(tr("drm_refused"))
        return

    if widevine and pre_auth and not widevine_ready():
        log(f"Playback stopped for asset={asset_id}: the title is DRM protected and "
            f"Widevine is not available on this system", xbmc.LOGWARNING)
        set_resolved_failed(tr("cdm_needed"))
        return

    item = xbmcgui.ListItem(path=url)
    item.setMimeType("application/vnd.apple.mpegurl")
    item.setContentLookup(False)

    position, total = resume_point(asset_id)
    if position > 0:
        item.setProperty("ResumeTime", str(position))
        item.setProperty("TotalTime", str(total or position + 1))
        try:
            item.getVideoInfoTag().setResumePoint(position, total or position + 1)
        except (AttributeError, TypeError):
            pass
        log(f"Resume point for asset={asset_id}: {int(position)}s of {int(total)}s",
            xbmc.LOGDEBUG)

    remember_episode_parent(api, asset_id)
    try:
        xbmcgui.Window(HOME_WINDOW).setProperty(PLAYING_PROPERTY, str(asset_id))
        log(f"Playing asset={asset_id}, published for playback tracking")
    except Exception as exc:
        log(f"Could not publish the playing asset id: {exc}", xbmc.LOGERROR)

    stream_headers = "&".join(
        [
            "User-Agent=" + quote(user_agent(), safe=""),
            "Origin=" + quote("https://eon.tv", safe=""),
            "Referer=" + quote("https://eon.tv/", safe=""),
        ]
    )

    item.setProperty("inputstream", "inputstream.adaptive")
    if kodi_major() < 21:
        item.setProperty("inputstream.adaptive.manifest_type", "hls")
    item.setProperty("inputstream.adaptive.stream_headers", stream_headers)
    item.setProperty("inputstream.adaptive.manifest_headers", stream_headers)

    if widevine and pre_auth:
        license_key = "{}|{}|R{{SSM}}|".format(
            widevine,
            "&".join(
                [
                    "PreAuthorization=" + quote(pre_auth, safe=""),
                    "User-Agent=" + quote(user_agent(), safe=""),
                    "Content-Type=application/octet-stream",
                ]
            ),
        )
        item.setProperty("inputstream.adaptive.license_type", "com.widevine.alpha")
        item.setProperty("inputstream.adaptive.license_key", license_key)
        log(f"Attached Widevine DRM for asset={asset_id}", xbmc.LOGDEBUG)
    else:
        log(f"No Widevine DRM attached for asset={asset_id} (clear stream or no pre-auth)",
            xbmc.LOGDEBUG)

    xbmcplugin.setResolvedUrl(HANDLE, True, item)


def require_session(api: EonApi) -> bool:
    if api.pvr_addon is None:
        xbmcgui.Dialog().ok(
            ADDON_NAME,
            "Install and configure pvr.eon first. EON On Demand uses the PVR add-on as the single login and device session owner.",
        )
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return False

    missing = []
    if not api.settings.access_token:
        missing.append("access token")
    if not api.settings.device_id:
        missing.append("device id")
    if not api.settings.stream_key:
        missing.append("stream key")
    if not api.settings.stream_user:
        missing.append("stream user")
    if not api.settings.device_number:
        missing.append("device number")
    if missing:
        xbmcgui.Dialog().ok(
            ADDON_NAME,
            "Open Live TV with pvr.eon first so it can log in and save the EON session. Missing: "
            + ", ".join(missing),
        )
        api.pvr_addon.openSettings()
        xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        return False
    return True


def main() -> None:
    params = dict(parse_qsl(sys.argv[2][1:]))
    mode = params.get("mode", "root")
    api = EonApi()

    set_category()
    if not require_session(api):
        return

    try:
        if mode == "root":
            list_root(api)
            xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
        elif mode == "tools":
            list_tools(api)
        elif mode == "sync":
            full = params.get("full") == "1"

            if not load_cache():
                question = tr("sync_ask")
            elif full:
                question = tr("sync_full_ask")
            else:
                question = ""

            background = params.get("background") == "1"
            if background:
                question = ""
            if params.get("confirm", "1") != "0" and question \
                    and not xbmcgui.Dialog().yesno(ADDON_NAME, question):
                xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
                return
            problem = pvr_status(api)
            if problem:
                if background:
                    notify(problem, 7000)
                else:
                    xbmcgui.Dialog().ok(ADDON_NAME, problem)
                xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
                return
            sync_cache(api, full_refresh=full, background=background)

            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            if not background:
                xbmc.executebuiltin("Container.Refresh")
        elif mode == "cache_type":
            list_cache_type(params["content_type"], params.get("section"))
        elif mode == "networks":
            list_networks(api)
        elif mode == "cache_info":
            show_cache_info()
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        elif mode == "account_info":
            show_account_info(api)
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
        elif mode == "cache_clear":
            if xbmcgui.Dialog().yesno(ADDON_NAME, tr("cache_clear_ask")):
                try:
                    if xbmcvfs.exists(CACHE_FILE):
                        xbmcvfs.delete(CACHE_FILE)
                    drop_legacy_cache()
                    notify(tr("cache_cleared"), 2000)
                except Exception as exc:
                    log(f"Could not clear the cache: {exc}", xbmc.LOGERROR)
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            xbmc.executebuiltin("Container.Refresh")
        elif mode == "search":
            list_search_root()
        elif mode == "search_new":
            query = (xbmcgui.Dialog().input(tr("search_prompt"), type=xbmcgui.INPUT_ALPHANUM) or "").strip()
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            if len(query) >= MIN_SEARCH_LENGTH:
                xbmc.executebuiltin(
                    f"Container.Update({plugin_url(mode='search_do', q=query)})")
        elif mode == "search_do":
            search_query = (params.get("q") or "").strip()
            if len(search_query) < MIN_SEARCH_LENGTH:
                list_search_root()
            else:
                list_search_results(api, search_query)
        elif mode == "search_clear":
            if xbmcgui.Dialog().yesno(ADDON_NAME, tr("search_clear_ask")):
                save_searches([])
                xbmc.executebuiltin("Container.Refresh")
        elif mode == "search_forget":
            gone = (params.get("q") or "").casefold()
            save_searches([q for q in load_searches() if q.casefold() != gone])
            xbmc.executebuiltin("Container.Refresh")
        elif mode == "go_back":
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)
            xbmc.executebuiltin("Action(ParentDir)")
        elif mode == "favorites":
            list_favorites()
        elif mode == "fav_add":
            payload = decode_data(params.get("payload") or "") or {}
            key = favorite_key(params.get("kind") or "asset", params.get("id"), params.get("season"))
            entries = [e for e in load_favorites() if e.get("key") != key]

            entries.insert(0, {"key": key, "kind": params.get("kind") or "asset",
                               "added": int(time.time()), "payload": payload})
            save_favorites(entries)
            notify(tr("fav_added"), 2000)
            xbmc.executebuiltin("Container.Refresh")
        elif mode == "fav_remove":
            key = params.get("key") or ""
            save_favorites([e for e in load_favorites() if e.get("key") != key])
            notify(tr("fav_removed"), 2000)
            xbmc.executebuiltin("Container.Refresh")
        elif mode == "fav_clear":
            if xbmcgui.Dialog().yesno("EON", tr("fav_clear_ask")):
                save_favorites([])
                notify(tr("fav_cleared"), 2000)
                xbmc.executebuiltin("Container.Refresh")
        elif mode == "stripes":
            list_stripes(params.get("section"))
        elif mode == "cache_category":
            list_cache_category(params["category"], int(params.get("page") or 0))
        elif mode == "catalogue":
            list_catalogue(api, params["id"], int(params.get("page") or 0))
        elif mode == "group_networks":
            list_group_networks(api, params["section"])
        elif mode == "cache_items":
            list_cache_items(params.get("content_type"), params.get("membership"),
                             params.get("section"), int(params.get("page", "0")),
                             params.get("kind"))
        elif mode == "asset":
            list_asset(api, params["id"])
        elif mode == "season":
            list_season(api, params["series"], params["season"])
        elif mode == "play":
            play(api, params["id"])
        else:
            xbmcplugin.endOfDirectory(HANDLE, cacheToDisc=CACHE_TO_DISC)
    except Exception as exc:
        log(f"Unhandled error in mode {mode}: {exc}", xbmc.LOGERROR)
        log(traceback.format_exc(), xbmc.LOGERROR)
        notify(str(exc), 7000)
        if mode == "play":
            set_resolved_failed(str(exc))
        else:
            xbmcplugin.endOfDirectory(HANDLE, succeeded=False)

if __name__ == "__main__":
    main()
    