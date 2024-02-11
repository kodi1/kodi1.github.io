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

import requests
from packaging import version
from packaging.version import InvalidVersion
from packaging_legacy import version as legacy_version

readme_text = "Last updated addons:  \n"
repo_folder = os.path.join(os.getcwd(), "repo")
requests.packages.urllib3.disable_warnings()
tmp_path = tempfile.mkdtemp(prefix='%s_tmp_' % os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0])


def get_repo_details(url):
    repo_owner = None
    repo_name = None
    try:
        matches = re.compile(r"github\.com/(.+?)/(.+?)/archive").findall(url)
        repo_owner = matches[0][0]
        repo_name = matches[0][1]
    except Exception as er:
        log(er)
        log("Not able to verify if there is a new version of the addon.")
    return repo_owner, repo_name


def get_addons_list():
    log("Loading addons list from addons.json")
    urls_list = json.load(open('addons.json'))
    log("Number of addons in list %s" % len(urls_list))
    addons = []
    for url in urls_list:
        owner, addon_name = get_repo_details(url)
        if addon_name:
            addons.append({
                "name": addon_name,
                "owner": owner,
                "url": url,
                "folder": os.path.join(repo_folder, addon_name),
                "xmlfile": os.path.join(repo_folder, addon_name, "addon.xml")
            })
    return addons


def get_remote_addon_version_string(repo_id, addon_id):
    try:
        url = "https://raw.githubusercontent.com/%s/%s/master/addon.xml" % (repo_id, addon_id)
        res = requests.get(url, verify=False)
        xml = etree.fromstring(res.content)
        return xml.get('version')
    except Exception as ex:
        log(ex)
    return None


def get_addon_version_from_xml_file(addon_xml_path):
    version_string = None
    try:
        xml = etree.parse(addon_xml_path)
        version_string = xml.getroot().get('version')
    except Exception as ex:
        log(ex)
    return version_string


def get_addon_version(version_string):
    try:
        return version.parse(version_string)
    except InvalidVersion:
        return legacy_version.parse(version_string)
    except Exception as ex:
        log(ex)
        return None


def is_updated(addon):
    log("\033[1;32m%s\033[0m" % addon["name"])
    log("Checking for new versions")
    local_addon_version_string = get_addon_version_from_xml_file(addon["xmlfile"])
    remote_addon_version_string = get_remote_addon_version_string(addon["owner"], addon["name"])
    log("Local version is %s, remote version is %s" % (local_addon_version_string, remote_addon_version_string))
    local_addon_version = get_addon_version(local_addon_version_string)
    remote_addon_version = get_addon_version(remote_addon_version_string)

    if not local_addon_version or not remote_addon_version:
        log("Due to version parsing failure, comparing version strings")
        if local_addon_version_string == remote_addon_version_string:
            log("Version strings are equal, no update required")
            return False
        log("Could not compare version strings. \033[1;32mUpdating addon anyway!\033[0m\n")
        return True

    if local_addon_version < remote_addon_version:
        addon["old_version"] = local_addon_version
        addon["new_version"] = remote_addon_version
        addon["update_time"] = time.strftime("%d.%m.%Y")
        log("\033[1;32mNew version for addon %s will be downloaded!\033[0m\n" % addon["name"])

        return True

    log("\033[0;31mNo new version available!\033[0m\n")
    return False


def download(addon):
    if not download_from_url(addon["url"]):
        return download_from_url(addon["url"])


def download_from_url(url):
    file_name = None
    try:
        r = requests.get(url, verify=False, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0'})
        rh = r.headers.get('content-disposition')
        if r.status_code == 200:
            if rh:
                file_name = os.path.join(tmp_path, rh.split('filename=')[1])
            else:
                file_name = os.path.join(tmp_path, url.split('/')[-1])
            log("Downloading: ", file_name)
            with open(file_name, "wb") as code:
                code.write(r.content)

    except Exception as er:
        log(er)

    return file_name


def copy_to_repo(addon_temp_file, addon):
    try:
        log("Extracting addon to temp folder %s" % tmp_path)
        zipfile.ZipFile(addon_temp_file).extractall(tmp_path)
        addon_temp_dir = os.path.join(tmp_path, os.path.splitext(addon_temp_file)[0])
        addon_xml = os.path.join(addon_temp_dir, 'addon.xml')
        addon_version = get_addon_version_from_xml_file(addon_xml)
        new_addon_zip_file_name = '%s-%s.zip' % (addon["name"], addon_version)
        new_addon_zip_file_path = os.path.join(addon["folder"], new_addon_zip_file_name)
        log("New addon zip file path: %s" % new_addon_zip_file_path)
        shutil.copy(addon_temp_file, new_addon_zip_file_path)
        log("Copying addon.xml to %s" % addon["folder"])
        shutil.copy(addon_xml, addon["folder"])
        log("Deleting addon temp dir")
        shutil.rmtree(addon_temp_dir)
    except Exception as er:
        log(er)


def is_orphan(addon_name, addons):
    for addon in addons:
        if addon_name == addon["name"]:
            return False
    return True


def delete_orphan_addon_folders(addons):
    count = 0
    addon_folders = [f for f in os.listdir(repo_folder) if
                     os.path.isdir(os.path.join(repo_folder, f)) and not f.startswith(".") and not f.startswith("_")]
    for addon_folder in addon_folders:
        if is_orphan(addon_folder, addons):
            log("Deleting directory of removed addon \033[0;31m%s\033[0m" % addon_folder)
            shutil.rmtree(os.path.join(repo_folder, addon_folder))
            count += 1
    return count


def get_xml_content(path):
    try:
        return etree.parse(path).getroot()
    except Exception as e:
        log("Excluding %s due to error: %s" % (path, e))
        return None


def generate_addonsxml(addons):
    """
    Iterate through all addons in the repository and copy each addon.xml to the repository addons.xml
    """
    addons_xml_content = etree.Element("addons")
    for addon in addons:
        addon_xml_content = get_xml_content(addon["xmlfile"])
        if addon_xml_content:
            addons_xml_content.append(addon_xml_content)
    etree.ElementTree(addons_xml_content).write(os.path.join(repo_folder, "addons.xml"), encoding="utf8")
    log("Generated addons.xml")


def generate_md5_file():
    try:
        md5sum = hashlib.md5()
        md5sum.update(open(os.path.join(repo_folder, "addons.xml"), "r", encoding="utf8").read().encode('utf-8'))
        newmd5sum = md5sum.hexdigest()
        log("new md5 sum: %s" % newmd5sum)
        with open(os.path.join(repo_folder, "addons.xml.md5"), "w", encoding="utf8") as file:
            file.write(newmd5sum)
    except Exception as e:
        log("An error occurred creating addons.xml.md5 file: %s" % e)

    log("Generated md5")


def update_last_update_time():
    with open('index.html') as file:
        text = file.read()
        last_update_time = time.strftime("%H:%M:%S - %d.%m.%Y")
        re.sub('>Last update: (.*?)<', last_update_time, text)
    log("Updated last update time: %s" % last_update_time)


def update_readme(updated_addons):
    log("Updating README.md")
    with open("README.md", "w") as w:
        for updated_addon in updated_addons:
            text = "%s | updated to %s (previously %s)  on %s \n" % (
                updated_addon["name"], updated_addon.get("new_version"), updated_addon.get("old_version"),
                updated_addon.get("update_time"))
            print(text)
            w.write(text)


def log(msg):
    print("%s | %s" % (time.strftime("%d.%m.%Y %H:%M:%S"), msg))
