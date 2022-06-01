# -*- coding: utf-8 -*-
import os
import re
import sys
import glob
import json
import time
import shutil
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import zipfile
import tempfile
import requests
import traceback
from addons_xml_generator import AddonsXmlGenerator
from lxml import etree
from packaging import version

file_skip = [
  re.compile(r'\.git*'),
  re.compile(r'README*'),
  re.compile(r'.*\.zip'),
  re.compile(r'VERSION'),
  re.compile(r'Makefile'),
  re.compile(r'.*\.pyo'),
  re.compile(r'.*\.rst'),
  re.compile(r'.*dbg.*'),
  ]

requests.packages.urllib3.disable_warnings()
tmp_path = tempfile.mkdtemp(prefix='%s_tmp_' % os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0])
cwd = os.getcwd()
files = ['changelog.txt', 'icon.*', 'addon.xml', 'fanart.*']
readme_text = "Last updated addons:\n"


def remove_temp_dir():
  print("Trying to remove temp directory %s" % tmp_path)
  if os.path.exists(tmp_path):
    try: shutil.rmtree(tmp_path)
    except Exception as er:
      print(er)


def mk_repo_trget_name(name):
  return re.sub( r"(-\w+\.zip|-[\d.]*\.zip|\.zip)", "", os.path.basename(os.path.basename(name)))


def make_zipfile(output_filename, source_dir):
  relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
  with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
    for root, dirs, files in os.walk(source_dir):
      # add directory (needed for empty dirs)
      zip.write(root, os.path.relpath(root, relroot))
      for file in files:
        if any(skip.match(file) for skip in file_skip):
          continue
        filename = os.path.join(root, file)
        if os.path.isfile(filename): # regular files only
          arcname = os.path.join(os.path.relpath(root, relroot), file)
          zip.write(filename, arcname)

def transfer_it(dest, src):
  if os.path.exists(dest):
    shutil.rmtree(dest)
  os.makedirs(dest)
  for f in files:
    for a in glob.iglob(os.path.join(src, f)):
      shutil.copyfile(a, os.path.join(dest, os.path.basename(a)))

  addon_xml = os.path.join(src, 'addon.xml')
  print("Parsing addon xml file: %s" % addon_xml)
  try:
    tree = etree.parse(addon_xml)
    tree.getroot().get('version')
    name_zip = '%s-%s.zip' % (os.path.basename(dest), tree.getroot().get('version'))
    name_zip = os.path.join(dest, name_zip)
    print(name_zip)
    make_zipfile(name_zip, src)
  except Exception as er:
    print("Error parsing file")
    print(er)

  print("Get ", os.listdir(dest))

andromeda_addons = []

def get_remote_addon_version(repo_id, addon_id):

  global andromeda_addons
  ver = None

  try:
    if repo_id == 'andromeda':
      # get the addon versions from the list of versions on the website
      if len(andromeda_addons) == 0:
        url = 'https://andromeda.eu.org/xbmc/'
        print("Getting list of Andromeda addons and versions (done only once)")
        source = requests.get(url, verify=False).text
        # extract the addon name and version i.e. <a href="plugin.video.anibg-0.0.1.zip">
        andromeda_addons = re.compile('href="(.+?)-(.+?)\.zip').findall(source)

      # iterate through all addons and find out the latest version for the current addon_id
      versions = [] #addon for addon in andromeda_addons if addon_id == addon[0]]
      for addon in andromeda_addons:
        if addon_id == addon[0]:
          versions.append(version.parse(addon[1]))
          
      # print (versions)
      versions.sort(reverse=True)
      # print (versions)
      ver = versions[0]
    else:
      url = "https://raw.githubusercontent.com/%s/%s/master/addon.xml" % (repo_id, addon_id)
      res = requests.get(url, verify=False)
      xml = etree.fromstring( res.content )
      ver = version.parse(xml.get('version'))

  except Exception as ex:
    print(ex)

  return ver

def get_local_addon_version(addon_id):
  try:
    path = os.path.join(addon_id, 'addon.xml')
    xml = etree.parse( path )
    ver = xml.getroot().get('version')
    return version.parse(ver)

  except:
    return None

def is_addon_updated(url):
  print ("**************************************************************************")
  try:
    # Check github based addons
    try:
      matches = re.compile("github\.com/(.+?)/(.+?)/archive").findall(url)
      repo_id = matches[0][0]
      addon_id = matches[0][1]
    except:
      # Check andromeda based addons
      matches = re.compile('kodipermalink/(.+?).zip').findall(url)
      addon_id = matches[0]
      repo_id = 'andromeda'
  except:
    print("Not able to verify if there is a new version of the addon.")
    return True

  print("Checking if addon %s is updated" % addon_id.upper())

  local_addon_version = get_local_addon_version(addon_id)
  remote_addon_version = get_remote_addon_version(repo_id, addon_id)

  if local_addon_version < remote_addon_version:
    global readme_text
    readme_text += "%s | updated to %s (previously %s)\n" % (addon_id, remote_addon_version, local_addon_version)
    print("Local version is %s, remote version is %s. Addon will be updated!" % (local_addon_version, remote_addon_version))
    return True

  print("Local version is %s, remote versions is %s. Skipping addon update!" % (local_addon_version, remote_addon_version))
  return False


def download_addon(url):
  try:
    r = requests.get(url, verify=False, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0'})
    rh = r.headers.get('content-disposition')
    if r.status_code == 200:
      if rh:
        f_name = os.path.join(tmp_path, rh.split('filename=')[1])
      else:
        f_name = os.path.join(tmp_path, url.split('/')[-1])
      print("Download: ", f_name)
      with open(f_name, "wb") as code:
        code.write(r.content)
    return True
  except:
    print(traceback.format_exc(sys.exc_info()))
    return False


def download_addons(urls):
  # Iterate the addons list and download only addons with newer version
  for url in urls:
    # Check if addon is new version
    if is_addon_updated(url):
      # if first download fails retry once
      if not download_addon(url):
        print('Download failed! Retrying...')
        download_addon(url)


def update_last_update_time():
  with open (os.path.join('../', 'index.html')) as file:
    text = file.read()
    last_update_text = time.strftime("%H:%M:%S - %d.%m.%Y")
    re.sub('>Last update: (.*?)<', last_update_text, text)

def update_readme():
  print ("Updating README")
  with open("../README.md", "w") as w:
    w.write(readme_text)


if ( __name__ == "__main__" ):
  
  print( "Using temp path %s" % tmp_path)
  print("Current working dir: %s" % cwd)
  addons_urls_list = json.load(open('addons.json'))
  print( "Loaded list of %s addon urls" % len(addons_urls_list))
  download_addons(addons_urls_list)
  print("**************************************************************************")
  print("Extracting addons that will be updated")
  for a in glob.iglob(os.path.join(tmp_path, '*.zip')):
    name = mk_repo_trget_name(a)

    new_name = os.path.join(tmp_path, name)
    old_name = os.path.join(tmp_path, os.path.splitext(a)[0])

    zfile = zipfile.ZipFile(a)
    zfile.extractall(tmp_path)

    if os.path.exists(old_name):
      print('%s -> %s' % (old_name, new_name))
      os.rename(old_name, new_name)

    transfer_it(os.path.join(cwd, name), os.path.join(tmp_path, name))

  remove_temp_dir()

  gen = AddonsXmlGenerator()
  gen.generate_repo_addonsxml()
  gen.generate_md5_file()
  print ("Finished updating addons xml and md5 files")
  print("Generating HTML page")

  update_last_update_time()
  update_readme()
  
  