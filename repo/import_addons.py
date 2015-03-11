#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import md5
import urllib
import urllib2
import requests
import addons_xml_generator as gen
import shutil
import tempfile
import glob
import zipfile
import re
from lxml import etree
import time

tmp_path = tempfile.mkdtemp(prefix='tmp_%s_' % os.path.splitext(os.path.basename(sys.modules['__main__'].__file__))[0])
cwd = os.getcwd()
files = ['changelog.txt', 'icon.*', 'addon.xml', 'fanart.*']

addons_url_list = [
    "https://github.com/kodi1/service.subtitles.unacs/archive/master.zip",
    "https://github.com/kodi1/plugin.video.kolibka/archive/next.zip",
    "https://github.com/kodi1/plugin.video.kmediatorrent/archive/master.zip",
    "https://www.andromeda.eu.org/xbmc/plugin.video.nova.play-0.1.1.zip",
    "https://www.andromeda.eu.org/xbmc/plugin.video.vbox7-0.3.5.zip",
  ]

def mk_repo_trget_name(name):
  return re.sub( r"(-.*zip)", "", os.path.basename(os.path.basename(name)))

def make_zipfile(output_filename, source_dir):
  relroot = os.path.abspath(os.path.join(source_dir, os.pardir))
  with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
    for root, dirs, files in os.walk(source_dir):
      # add directory (needed for empty dirs)
      zip.write(root, os.path.relpath(root, relroot))
      for file in files:
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

  tree = etree.parse(os.path.join(src, 'addon.xml'))
  tree.getroot().get('version')

  name_zip = '%s-%s.zip' % (os.path.basename(dest), tree.getroot().get('version'))
  name_zip = os.path.join(dest, name_zip)
  print name_zip
  make_zipfile(name_zip, src)

  print "Get ", os.listdir(dest)

def import_addons (list):
  for l in list:
    r = requests.get(l)
    rh = r.headers.get('content-disposition')
    if r.status_code == 200:
      if rh:
        f_name = os.path.join(tmp_path, rh.split('filename=')[1])
      else:
        f_name = os.path.join(tmp_path, l.split('/')[-1])

      print "Download: ", f_name
      with open(f_name, "wb") as code:
        code.write(r.content)

if ( __name__ == "__main__" ):
  # start
  import_addons(addons_url_list)

  for a in glob.iglob(os.path.join(tmp_path, '*.zip')):
    name = mk_repo_trget_name(a)

    new_name = os.path.join(tmp_path, name)
    old_name = os.path.join(tmp_path, os.path.splitext(a)[0])

    zfile = zipfile.ZipFile(a)
    zfile.extractall(tmp_path)

    if os.path.exists(old_name):
      os.rename(old_name, new_name)

    transfer_it(os.path.join(cwd, name), os.path.join(tmp_path, name))

  if os.path.exists(tmp_path):
    shutil.rmtree(tmp_path)

  gen.Generator()

  parser = etree.HTMLParser()
  tree   = etree.parse(os.path.join('../', 'index.html'), parser)
  for s in tree.getroot().iter('p'):
    if s.text:
      if s.text.split(':')[0] == 'Last update':
        s.text = 'Last update: %s' % time.strftime("%H:%M:%S - %d.%m.%Y")
        print s.text

  tree.write(os.path.join('../', 'index.html'), method="html", pretty_print=True)