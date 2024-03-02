import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
import time
import xml.etree.ElementTree as etree
from enum import Enum

import requests

__force_global_update = False
__repo_folder = os.path.join(os.getcwd(), "repo")
requests.packages.urllib3.disable_warnings()
__backup_folder_suffix = "_backup"
__temp_dir = None


class LogLevel(Enum):
    ERROR = 4
    WARN = 3
    INFO = 2
    DEBUG = 1


__default_loglevel = LogLevel.DEBUG


def log(msg, loglevel=LogLevel.INFO):
    if loglevel.value >= __default_loglevel.value:
        if loglevel == LogLevel.WARN:
            loglevelstring = "\033[1;33m%s\033[0m" % loglevel.name.upper()
            msg = "\033[0;33m%s\033[0m" % msg
        elif loglevel == LogLevel.ERROR:
            loglevelstring = "\033[0;31m%s\033[0m" % loglevel.name.upper()
            msg = "\033[0;31m%s\033[0m" % msg
        elif loglevel == LogLevel.INFO:
            loglevelstring = "\033[1;32m%s\033[0m" % loglevel.name.upper()
        else:
            loglevelstring = loglevel.name.upper()
        print("%s | %s | %s" % (time.strftime("%d.%m.%Y %H:%M:%S"), loglevelstring, msg))


def get_temp_folder():
    """
    Returns the temp folder where all addons will be extracted
    """
    global __temp_dir
    if not __temp_dir:
        __temp_dir = tempfile.mkdtemp(
            prefix='%s_tmp_' % os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0])
    return __temp_dir


def get_enabled_addons():
    """
    Loads the list of addons from addons.json and returns ONLY the enabled addons
    """
    log("Loading addons list from addons.json")
    addons = json.load(open('addons.json'))
    enabled_addons = []
    disabled_addons_count = 0
    for addon in addons:
        if addon.get("enabled", True):
            addon["folder"] = os.path.join(__repo_folder, addon["name"])
            addon["xmlfile"] = os.path.join(__repo_folder, addon["name"], "addon.xml")
            enabled_addons.append(addon)
        else:
            disabled_addons_count += 1
    log("Number of enabled addons in list %s" % len(addons))
    log("Number of disabled addons in list %s" % disabled_addons_count)
    return enabled_addons


def __build_remote_addon_xml_url(addon):
    """
    Builds the URL to the remote addon.xml. Currently supports only github, gitlab
    """
    repo_name = addon.get("repo_name") if addon.get("repo_name") else addon["name"]

    if addon["provider"] == "github":
        return "https://raw.githubusercontent.com/%s/%s/master/addon.xml" % (addon["owner"], repo_name)
    elif addon["provider"] == "gitlab":
        return "https://gitlab.com/%s/%s/-/raw/master/addon.xml" % (addon["owner"], repo_name)
    raise Exception("Unknown addon provider for %s" % addon["name"])


def __get_remote_addon_version_string(addon):
    try:
        remote_url = addon.get("remote_xml_url")
        if not remote_url:
            remote_url = __build_remote_addon_xml_url(addon)
            log("Getting remote addon version from url: %s" % remote_url, LogLevel.DEBUG)
            if not remote_url:
                log("No remote xml provided for version comparison")
                return None

        res = requests.get(remote_url, verify=False)
        xml = etree.fromstring(res.content)
        return xml.get('version')
    except Exception as ex:
        log("Error getting remote version: %s" % ex, LogLevel.ERROR)
    return None


def __get_addon_version_from_xml_file(addon_xml_path):
    version_string = None
    try:
        xml = etree.parse(addon_xml_path)
        version_string = xml.getroot().get('version')
    except Exception as ex:
        log(ex, LogLevel.ERROR)
    return version_string


def should_update(addon):
    log("\033[1;32m%s\033[0m" % addon["name"])
    if __force_global_update:
        log("Force updating all addons due to force_global_update=True")
        return True
    if addon.get("force_update", False):
        log("Force updating addon due to addon setting force_update=True")
        return True
    if not addon.get("update", True):
        if os.path.exists(addon["folder"]) and os.path.exists(addon["xmlfile"]):
            log("Skipping automatic update as update property is disabled", LogLevel.WARN)
            return False
        else:
            log("Update property is set to false, but addon seems to be missing, so force updating it", LogLevel.WARN)
            return True
    if not os.path.exists(addon["folder"]):
        log("No local version found. Adding addon", LogLevel.WARN)
        return True

    addon["version"] = __get_addon_version_from_xml_file(addon["xmlfile"])
    if not addon.get("version"):
        log("Unable to detect addon local version. Updating addon.")
        return True

    log("Checking for addon new versions")
    addon["new_version"] = __get_remote_addon_version_string(addon)

    if addon.get("version") is None and addon.get("new_version") is None:
        log("Unable to detect local and remote addon versions. Updating addon anyway.")
        return True

    log("Local version is %s, remote version is %s" % (addon["version"], addon["new_version"]))
    if addon.get("version") != addon.get("new_version"):
        log("\033[1;32mRemote version for addon %s is different than local. Updating addon!\033[0m" % addon["name"])
        return True

    log("No new version available!")
    return False


def __build_download_url(addon):
    """
    Build addon zip url given the provider - github or gitlab
    """
    provider = addon.get("provider")

    if provider:
        repo_name = addon.get("repo_name")
        if not repo_name:
            repo_name = addon["name"]

        if provider.lower() == "github":
            return "https://github.com/%s/%s/archive/master.zip" % (addon["owner"], repo_name)
        elif provider.lower() == "gitlab":
            return "https://gitlab.com/%s/%s/-/archive/master/weather.multi-master.zip" % (addon["owner"], repo_name)

    raise Exception("No provider provided for addon %s" % addon["name"])


def download(addon):
    try:
        url = addon.get('url')
        if url is None:
            url = __build_download_url(addon)
        addon["temp_file"] = __download_from_url(url, get_temp_folder())
        if not addon.get("temp_file"):
            addon["temp_file"] = __download_from_url(url, get_temp_folder())
        return True
    except Exception as er:
        log(er, LogLevel.ERROR)
        return False


def __download_from_url(url, temp_folder):
    """
    Downloads zip from URL and returns the absolute path to the downloaded local file
    """
    file_path = None
    log("Downloading zip from url %s" % url)
    try:
        r = requests.get(url, verify=False, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/121.0.0.0 Safari/537.36'})
        if r.status_code == 200:
            file_path = os.path.join(temp_folder, url.split('/')[-1])
            log("Downloading: %s" % file_path)
            with open(file_path, "wb") as code:
                code.write(r.content)

    except Exception as er:
        log(er)

    log("Saved file locally %s" % file_path)
    return file_path


def __get_addon_folder_path(extract_folder):
    """
    Provides the absolute path to the extracted addon folder containing the addon.xml
    It is required as some addons reside in nested folders
    """
    for folder in os.listdir(extract_folder):
        if folder.startswith(".") or folder.startswith("_"):
            continue
        absolute_folder_path = os.path.join(extract_folder, folder)
        if not os.path.isdir(absolute_folder_path):
            continue
        addon_xml_path = os.path.join(absolute_folder_path, "addon.xml")
        if os.path.isfile(addon_xml_path):
            return absolute_folder_path


def __get_extracted_folder(addon_temp_file):
    temp_file_name = os.path.splitext(addon_temp_file)[0]
    return os.path.join(get_temp_folder(), temp_file_name)


def __extract(addon):
    """
    Extract the addon archive to a separate folder, so we can easier find the addon.xml
    This is necessary because some addon ZIP file names are different from the addon name
    """
    addon["work_folder"] = __get_extracted_folder(addon["temp_file"])
    zipfile.ZipFile(addon["temp_file"]).extractall(addon["work_folder"])
    addon["temp_folder"] = __get_addon_folder_path(addon["work_folder"])
    log("Extracted addon to temp folder %s" % addon["temp_folder"])


def __generate_new_addon_file_name(addon_name, addon_version):
    return '%s-%s.zip' % (addon_name, addon_version)


def try_delete_folder(folder):
    try:
        log("Deleting folder %s" % folder, LogLevel.DEBUG)
        if os.path.exists(folder):
            shutil.rmtree(folder)
    except Exception as er:
        log(er, LogLevel.ERROR)


def __generate_new_archive_filename(addon):
    if not addon.get("new_version"):
        addon["new_version"] = __get_addon_version_from_xml_file(os.path.join(addon["temp_folder"], "addon.xml"))
    return __generate_new_addon_file_name(addon["name"], addon["new_version"])


def update(addon):
    try:
        __extract(addon)
        backup_folder = addon["folder"] + __backup_folder_suffix
        renamed_addon_archive_filename = __generate_new_archive_filename(addon)

        try_delete_folder(backup_folder)
        if os.path.exists(addon["folder"]):
            shutil.move(addon["folder"], backup_folder)
        try:
            shutil.move(addon["temp_folder"], addon["folder"])
            shutil.move(addon['temp_file'], os.path.join(addon["folder"], renamed_addon_archive_filename))
        except Exception as er:
            log("Error during addon copy operations: %s" % er)
            if os.path.exists(backup_folder) and not os.path.exists(addon["folder"]):
                log("Restoring addon backup")
                shutil.move(backup_folder, addon["folder"])

        try_delete_folder(backup_folder)
        try_delete_folder(addon["work_folder"])

        log("Updated addon \033[1;32m to version %s\033[0m " % (addon.get("new_version")))
        addon["update_time"] = time.strftime("%d.%m.%Y")

        return True
    except Exception as er:
        log(er, LogLevel.ERROR)
        return False


def __is_orphan(addon_name, addons):
    for addon in addons:
        if addon_name == addon["name"]:
            return False
    return True


def delete_orphan_addon_folders(addons):
    log("Checking for orphan folders to delete")
    count = 0
    addon_folders = [f for f in os.listdir(__repo_folder) if
                     os.path.isdir(os.path.join(__repo_folder, f)) and not f.startswith(".") and not f.startswith("_")]
    for addon_folder in addon_folders:
        if addon_folder.endswith(__backup_folder_suffix) or __is_orphan(addon_folder, addons):
            log("Deleting \033[0;31m%s\033[0m" % addon_folder)
            shutil.rmtree(os.path.join(__repo_folder, addon_folder))
            count += 1
    return count


def __get_xml_content(path):
    try:
        return etree.parse(path).getroot()
    except Exception as e:
        log("Excluding %s due to error: %s" % (path, e), LogLevel.ERROR)
        return None


def generate_addons_xml_file(addons):
    """
    Iterate through all addons in the repository and copy each addon.xml to the repository addons.xml
    """
    addons_xml_content = etree.Element("addons")
    for addon in addons:
        addon_xml_content = __get_xml_content(addon["xmlfile"])
        if not addon_xml_content:
            continue
        addon_id = addon_xml_content.get('id')
        if addon["name"] != addon_id:
            raise Exception("ERROR addon name/id mismatch %s/%s" % (addon["name"], addon_id))
        if addon_xml_content:
            addons_xml_content.append(addon_xml_content)
    etree.ElementTree(addons_xml_content).write(os.path.join(__repo_folder, "addons.xml"), encoding="utf8")
    log("Generated addons.xml")


def generate_md5_file():
    try:
        md5sum = hashlib.md5()
        md5sum.update(open(os.path.join(__repo_folder, "addons.xml"), "r", encoding="utf8").read().encode('utf-8'))
        newmd5sum = md5sum.hexdigest()
        log("new md5 sum: %s" % newmd5sum)
        with open(os.path.join(__repo_folder, "addons.xml.md5"), "w", encoding="utf8") as file:
            file.write(newmd5sum)
    except Exception as e:
        log("An error occurred creating addons.xml.md5 file: %s" % e, LogLevel.ERROR)

    log("Generated md5")


def update_last_update_time():
    text = None
    with open("index.html", "r", encoding="utf8") as f:
        text = f.read()
    with open("index.html", "w", encoding="utf8") as f:
        last_update_time = time.strftime("%H:%M:%S - %d.%m.%Y")
        last_update_text = ">Last update: %s<" % last_update_time
        text = re.sub('>Last update: (.*?)<', last_update_text, text)
        f.write(text)
        log("Updated last update time: %s" % last_update_time)


def update_readme(updated_addons):
    log("Updating README.md")
    with open("README.md", "w") as file_handle:
        for updated_addon in updated_addons:
            text = "%s | updated to %s on %s \n" % (
                updated_addon["name"], updated_addon.get("new_version"), updated_addon.get("update_time"))
            print(text)
            file_handle.write(text)
