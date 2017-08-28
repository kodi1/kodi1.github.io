#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import md5
import glob
import json
import time
import shutil
import urllib
import urllib2
import zipfile
import tempfile
import requests
import traceback
import addons_xml_generator as gen
from lxml import etree

file_skip = [
              re.compile(r'\.git*'),
#              re.compile(r'LICENSE*'),  #Removed as license files need to be included in addons
              re.compile(r'README*'),
#              re.compile(r'.*\.txt'), #Removed as it prevents changelog.txt from being included
              re.compile(r'.*\.zip'),
              re.compile(r'VERSION'),
              re.compile(r'Makefile'),
              re.compile(r'.*\.pyo'),
              re.compile(r'.*\.rst'),
              re.compile(r'.*dbg.*'),
              ]

tmp_path = tempfile.mkdtemp(prefix='%s_tmp_' % os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0])
print "Using temp path %s" % tmp_path
cwd = os.getcwd()
files = ['changelog.txt', 'icon.*', 'addon.xml', 'fanart.*']
addons_urls_list = json.load(open('addons.json'))
print "Loaded list of %s addon urls" % len(addons_urls_list)

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
    #do cleanup
    shutil.rmtree(dest)
  os.makedirs(dest)
  for f in files:
    for a in glob.iglob(os.path.join(src, f)):
      shutil.copyfile(a, os.path.join(dest, os.path.basename(a)))

  addon_xml = os.path.join(src, 'addon.xml')
  print "Parsing addon xml file:" + addon_xml
  try:
    tree = etree.parse(addon_xml)
    tree.getroot().get('version')
    name_zip = '%s-%s.zip' % (os.path.basename(dest), tree.getroot().get('version'))
    name_zip = os.path.join(dest, name_zip)
    print name_zip
    make_zipfile(name_zip, src)
  except Exception as er:
    print "Error parsing file"
    print str(er)

  print "Get ", os.listdir(dest)

def get_remote_addon_version(repo_id, addon_id):
  try:
    url = "https://raw.githubusercontent.com/%s/%s/master/addon.xml" % (repo_id, addon_id)
    res = requests.get(url)
    xml = etree.fromstring( res.content )
    version = xml.get('version')
    return version

  except:
    return None

def get_local_addon_version(addon_id):
  try:
    path = os.path.join(addon_id, 'addon.xml')
    xml = etree.parse( path )
    version = xml.getroot().get('version')
    return version

  except:
    return None

def is_addon_updated(url):
  try:
    # Check only github based addons
    matches = re.compile("github\.com/(.*?)/(.+?)/archive").findall(url)

    repo_id = matches[0][0]
    addon_id = matches[0][1]

    local_addon_version = get_local_addon_version(addon_id)
    remote_addon_version = get_remote_addon_version(repo_id, addon_id)

    if local_addon_version != remote_addon_version:
      print "Addon %s has been updated. New version is %s" % (addon_id, remote_addon_version)
      return True
    print "Addon %s has not been updated and will not be downloaded. Version is %s" % (addon_id, local_addon_version)
    return False

  except:
    print "Not able to verify if addon was updated. Downloading it anyway."
    return True

def download_addon(url):
  #print 'Get url: %s' % url
  try:
    r = requests.get(url, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0'})
    rh = r.headers.get('content-disposition')
    if r.status_code == 200:
      if rh:
        f_name = os.path.join(tmp_path, rh.split('filename=')[1])
      else:
        f_name = os.path.join(tmp_path, url.split('/')[-1])
      print "Download: ", f_name
      with open(f_name, "wb") as code:
        code.write(r.content)
    return True
  except:
    print traceback.format_exc(sys.exc_info())
    return False

def download_addons(urls):
  # Iterate the addons list and download only addons with newer version
  for url in urls:
    # Check if addon is new version
    if is_addon_updated(url):
      # if first download fails retry once
      if not download_addon(url):
        print 'Download failed! Retrying...'
        download_addon(url)
    print "*********************************"


if ( __name__ == "__main__" ):
  # start
  download_addons(addons_urls_list)

  for a in glob.iglob(os.path.join(tmp_path, '*.zip')):
    name = mk_repo_trget_name(a)

    new_name = os.path.join(tmp_path, name)
    old_name = os.path.join(tmp_path, os.path.splitext(a)[0])

    zfile = zipfile.ZipFile(a)
    zfile.extractall(tmp_path)

    if os.path.exists(old_name):
      print '%s -> %s' % (old_name, new_name,)
      os.rename(old_name, new_name)

    transfer_it(os.path.join(cwd, name), os.path.join(tmp_path, name))

  if os.path.exists(tmp_path):
    try: shutil.rmtree(tmp_path)
    except Exception, er:
      print str(er)

  gen.Generator()

  parser = etree.HTMLParser()
  tree   = etree.parse(os.path.join('../', 'index.html'), parser)
  for s in tree.getroot().iter('p'):
    if s.text:
      if s.text.split(':')[0] == 'Last update':
        s.text = 'Last update: %s' % time.strftime("%H:%M:%S - %d.%m.%Y")
        print s.text

  tree.write(os.path.join('../', 'index.html'), method="html", pretty_print=True)
