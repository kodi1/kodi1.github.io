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


def get_addons_list():
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


def get_remote_addon_version_string(addon):
    if "github" not in addon["url"]:
        return None

    try:
        url = "https://raw.githubusercontent.com/%s/%s/master/addon.xml" % (addon["owner"], addon["name"])
        res = requests.get(url, verify=False)
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
    if not addon.get("update", True):
        log("Skipping automatic update as update property is disabled\n")
        return False

    log("Checking for new versions")
    local_addon_version_string = get_addon_version_from_xml_file(addon["xmlfile"])
    remote_addon_version_string = get_remote_addon_version_string(addon)
    log("Local version is %s, remote version is %s" % (local_addon_version_string, remote_addon_version_string))
    local_addon_version = get_addon_version(local_addon_version_string)
    remote_addon_version = get_addon_version(remote_addon_version_string)

    if not local_addon_version and not remote_addon_version:
        log("Unable to detect local and remote addon versions. Updating it.")
        return True

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
    local_file = download_from_url(addon["url"])
    if not local_file:
        local_file = download_from_url(addon["url"])
    return local_file


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
            log("Downloading: %s" % file_name)
            with open(file_name, "wb") as code:
                code.write(r.content)

    except Exception as er:
        log(er)

    return file_name


def get_addon_xml_path(extract_folder):
    """
    Function that provides the absolute path of the extracted addon folder containing the addon.xml
    """
    for folder in os.listdir(extract_folder):
        if folder.startswith(".") or folder.startswith("_"):
            continue
        absolute_folder_path = os.path.join(extract_folder, folder)
        if not os.path.isdir(absolute_folder_path):
            continue
        addon_xml_path = os.path.join(absolute_folder_path, "addon.xml")
        if os.path.isfile(addon_xml_path):
            return addon_xml_path


def get_temp_addon_extract_folder(addon_temp_file):
    temp_file_name = os.path.splitext(addon_temp_file)[0]
    return os.path.join(tmp_path, temp_file_name)


def extract_addon_archive_to_folder(temp_addon_file, temp_addon_extract_folder):
    """
    Extract the addon archive to a separate folder, so we can easier find the addon.xml
    This is necessary because some addon ZIP file names are different from the addon name
    """
    log("Extracting addon to temp folder %s" % temp_addon_extract_folder)
    zipfile.ZipFile(temp_addon_file).extractall(temp_addon_extract_folder)


def create_new_addon_file_name(addon_name, addon_version):
    return '%s-%s.zip' % (addon_name, addon_version)


def delete_temp_files(temp_addon_file):
    try:
        log("Deleting addon temp files")
        shutil.rmtree(get_temp_addon_extract_folder(temp_addon_file))
        os.unlink(temp_addon_file)
    except:
        pass


def extract_addon_content(addon_name, addon_temp_file):
    """
    Extracts addon and renames it as per the version in addon.xml
    @returns: A tuple containing the path to the addon archive zip and the path to the addon.xml
    """
    personal_addon_extract_folder = get_temp_addon_extract_folder(addon_temp_file)
    extract_addon_archive_to_folder(addon_temp_file, personal_addon_extract_folder)
    temp_addon_xml_path = get_addon_xml_path(personal_addon_extract_folder)

    return temp_addon_xml_path


def copy_file(source_file, destination_file):
    dst_folder = os.path.dirname(destination_file)

    if not os.path.exists(dst_folder):
        log("Creating addon folder as it does not exist %s" % dst_folder)
        os.makedirs(dst_folder)

    shutil.copy(source_file, destination_file)


#
#
# def copy_to_repo(addon_temp_file, addon):
#     """
#     Renames addon zip to include addon version.
#     Copies the new addon zip and the extracted addon.xml to the repository folder
#     """
#     try:
#         temp_addon_dir = extract_addon_archive_to_folder(addon_temp_file)
#
#         temp_addon_xml = os.path.join(temp_addon_dir, 'addon.xml')
#         log("Copying addon.xml to %s" % addon["folder"])
#         shutil.copy(temp_addon_xml, addon["folder"])
#
#         new_addon_zip_file_name = create_new_addon_file_name(addon, temp_addon_xml)
#         new_addon_zip_file_path = os.path.join(addon["folder"], new_addon_zip_file_name)
#         log("New addon zip file path: %s" % new_addon_zip_file_path)
#         if not os.path.isdir(addon["folder"]):
#             log("Creating addon folder as it does not exist %s" % addon["folder"])
#             os.mkdir(addon["folder"])
#         shutil.copy(addon_temp_file, new_addon_zip_file_path)
#
#         delete_temp_files(addon_temp_file)
#     except Exception as er:
#         log(er)


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
            text = "%s | updated to %s (previously %s)  on %s \n" % (
                updated_addon["name"], updated_addon.get("new_version"), updated_addon.get("old_version"),
                updated_addon.get("update_time"))
            print(text)
            file_handle.write(text)


def log(msg):
    print("%s | %s" % (time.strftime("%d.%m.%Y %H:%M:%S"), msg))
