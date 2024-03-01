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

force_global_update = False
repo_folder = os.path.join(os.getcwd(), "repo")
requests.packages.urllib3.disable_warnings()
temp_dir = None


def get_temp_folder():
    """
    Returns the temp folder where all addons will be extracted
    """
    global temp_dir
    if not temp_dir:
        temp_dir = tempfile.mkdtemp(
            prefix='%s_tmp_' % os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0])
    return temp_dir


def get_addons_list():
    """
    Loads the list of addons from addons.json and returns ONLY the enabled addons
    """
    log("Loading addons list from addons.json")
    addons = json.load(open('addons.json'))
    enabled_addons = []
    disabled_addons_count = 0
    for addon in addons:
        if addon.get("enabled", True):
            addon["folder"] = os.path.join(repo_folder, addon["name"])
            addon["xmlfile"] = os.path.join(repo_folder, addon["name"], "addon.xml")
            enabled_addons.append(addon)
        else:
            disabled_addons_count += 1
    log("Number of enabled addons in list %s" % len(addons))
    log("Number of disabled addons in list %s\n" % disabled_addons_count)
    return enabled_addons


def build_remote_addon_xml_url(addon):
    """
    Builds the URL to the remote addon.xml. Currently supports only github, gitlab
    """
    repo_name = addon.get("repo_name") if addon.get("repo_name") else addon["name"]

    if addon["provider"] == "github":
        return "https://raw.githubusercontent.com/%s/%s/master/addon.xml" % (addon["owner"], repo_name)
    elif addon["provider"] == "gitlab":
        return "https://gitlab.com/%s/%s/-/raw/master/addon.xml" % (addon["owner"], repo_name)
    raise Exception("Unknown addon provider for %s" % addon["name"])


def get_remote_addon_version_string(addon):
    try:
        remote_url = addon.get("remote_xml_url")
        if not remote_url:
            remote_url = build_remote_addon_xml_url(addon)
            if not remote_url:
                log("No remote xml provided for version comparison")
                return None

        res = requests.get(remote_url, verify=False)
        xml = etree.fromstring(res.content)
        return xml.get('version')
    except Exception as ex:
        log("Error getting remote version: %s" % ex)
    return None


def get_addon_version_from_xml_file(addon_xml_path):
    version_string = None
    try:
        xml = etree.parse(addon_xml_path)
        version_string = xml.getroot().get('version')
    except Exception as ex:
        log(ex)
    return version_string


def should_updated(addon):
    log("\033[1;32m%s\033[0m" % addon["name"])
    if force_global_update:
        log("Force updating all addons due to force_global_update=True")
        return True
    if addon.get("force_update", False):
        log("Force updating addon due to addon setting force_update=True")
        return True
    if not addon.get("update", True):
        log("Skipping automatic update as update property is disabled\n")
        return False

    log("Checking for addon new versions")
    addon["version"] = get_addon_version_from_xml_file(addon["xmlfile"])
    addon["new_version"] = get_remote_addon_version_string(addon)

    if addon.get("version") is None and addon.get("new_version") is None:
        log("Unable to detect local and remote addon versions. Updating addon anyway.")
        return True

    log("Local version is %s, remote version is %s" % (addon["version"], addon["new_version"]))
    if addon.get("version") != addon.get("new_version"):
        log("\033[1;32mRemote version for addon %s is different than local. Updating addon!\033[0m" % addon["name"])
        return True

    log("\033[0;31mNo new version available!\033[0m\n")
    return False


def build_download_url(addon):
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


def download(addon, temp_folder):
    url = addon.get('url')
    if url is None:
        url = build_download_url(addon)
    local_file = download_from_url(url, temp_folder)
    if not local_file:
        local_file = download_from_url(url, temp_folder)
    return local_file


def download_from_url(url, temp_folder):
    file_name = None
    try:
        r = requests.get(url, verify=False, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/121.0.0.0 Safari/537.36'})
        if r.status_code == 200:
            file_name = os.path.join(temp_folder, url.split('/')[-1])
            log("Downloading: %s" % file_name)
            with open(file_name, "wb") as code:
                code.write(r.content)

    except Exception as er:
        log(er)

    return file_name


def resolve_addon_xml_folder(extract_folder):
    """
    Function that provides the absolute path of the extracted addon folder containing the addon.xml
    It is required as some addon are nested into a separate folder
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


def get_temp_addon_extract_folder(addon_temp_file):
    temp_file_name = os.path.splitext(addon_temp_file)[0]
    return os.path.join(get_temp_folder(), temp_file_name)


def extract_addon_archive_to_folder(temp_addon_file, temp_addon_extract_folder):
    """
    Extract the addon archive to a separate folder, so we can easier find the addon.xml
    This is necessary because some addon ZIP file names are different from the addon name
    """
    log("Extracting addon to temp folder %s" % temp_addon_extract_folder)
    zipfile.ZipFile(temp_addon_file).extractall(temp_addon_extract_folder)

    return resolve_addon_xml_folder(temp_addon_extract_folder)


def create_new_addon_file_name(addon_name, addon_version):
    return '%s-%s.zip' % (addon_name, addon_version)


def delete_temp_files(temp_addon_file):
    try:
        log("Deleting addon temp files")
        shutil.rmtree(get_temp_addon_extract_folder(temp_addon_file))
        os.unlink(temp_addon_file)
    except:
        pass


def delete_folder(folder):
    try:
        log("Deleting addon temp folder %s" % folder)
        shutil.rmtree(folder)
    except Exception as er:
        log(er)


def extract_addon_content(addon_name, addon_temp_file):
    """
    Extracts addon and renames it as per the version in addon.xml
    @returns: A the path to the addon's addon.xml
    """
    addon_extract_folder = get_temp_addon_extract_folder(addon_temp_file)
    folder_containing_addon_xml = extract_addon_archive_to_folder(addon_temp_file, addon_extract_folder)
    return folder_containing_addon_xml


def copy_file(source_file, destination_file):
    dst_folder = os.path.dirname(destination_file)

    if not os.path.exists(dst_folder):
        log("Creating addon folder as it does not exist %s" % dst_folder)
        os.makedirs(dst_folder)
    if os.path.isfile(source_file):
        shutil.copy(source_file, destination_file)


def is_orphan(addon_name, addons):
    for addon in addons:
        if addon_name == addon["name"]:
            return False
    return True


def delete_orphan_addon_folders(addons):
    log("Checking for orphan folders to delete")
    count = 0
    addon_folders = [f for f in os.listdir(repo_folder) if
                     os.path.isdir(os.path.join(repo_folder, f)) and not f.startswith(".") and not f.startswith("_")]
    for addon_folder in addon_folders:
        if is_orphan(addon_folder, addons):
            log("Deleting \033[0;31m%s\033[0m" % addon_folder)
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
        addon_id = addon_xml_content.get('id')
        if addon["name"] != addon_id:
            raise Exception("ERROR addon name/id mismatch %s/%s" % (addon["name"], addon_id))
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


def log(msg):
    print("%s | %s" % (time.strftime("%d.%m.%Y %H:%M:%S"), msg))
