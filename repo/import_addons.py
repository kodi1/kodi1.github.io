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
cwd = os.getcwd()
files = ['changelog.txt', 'icon.*', 'addon.xml', 'fanart.*']

addons_url_list = [
    "https://github.com/kodi1/plugin.program.braviacontrol/archive/master.zip",
    "https://github.com/kodi1/plugin.video.zelka/archive/master.zip",
    "https://github.com/kodi1/plugin.video.zamunda/archive/master.zip",
    "https://github.com/kodi1/service.subtitles.unacs/archive/master.zip",
    "https://github.com/kodi1/service.backlight.led/archive/master.zip",
    "https://github.com/kodi1/plugin.program.bscfusion/archive/master.zip",
    "https://github.com/kodi1/script.module.garepobg/archive/master.zip",
    "https://github.com/kodi1/plugin.video.kolibka/archive/next.zip",
    "https://github.com/kodi1/service.screensaver.hooks/archive/master.zip",
    "https://github.com/kodi1/service.sleeptimer/archive/master.zip",
    "https://github.com/kodi1/plugin.video.1channel/archive/master.zip",
    "https://github.com/enen92/service.pvrtools/archive/master.zip",
    "https://github.com/sasbass/plugin.video.mytv_bg/archive/master.zip",
    "https://github.com/mrolix/plugin.video.neterratv/archive/master.zip",
    "https://github.com/harrygg/plugin.video.free.bgtvs/archive/master.zip",
    "https://github.com/harrygg/plugin.video.gospodari/archive/master.zip",
    "https://github.com/harrygg/plugin.video.bgcameras/archive/master.zip",
    "https://github.com/harrygg/plugin.video.gong.play/raw/master/plugin.video.gong.play.zip",
    "https://github.com/harrygg/plugin.video.slavishow/raw/master/plugin.video.slavishow.zip",
    "https://github.com/harrygg/plugin.video.btvplus/archive/master.zip",
    "https://github.com/harrygg/plugin.program.freebgtvs/archive/master.zip",
    "https://github.com/harrygg/plugin.program.tvbgpvr.backend/archive/master.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.brigada.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.nova.play.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.vbox7.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.anibg.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.dramafever.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.vikir.zip",
    "https://andromeda.eu.org/kodipermalink/plugin.video.tubi.zip",
    "https://andromeda.eu.org/kodipermalink/script.module.urlresolver.zip",
    "https://andromeda.eu.org/kodipermalink/service.subtitles.bukvibg.zip",
    "https://github.com/Eldorados/script.module.axel.downloader/archive/master.zip",
    "https://github.com/Eldorados/eldorado-xbmc-addons/raw/master/repo/plugin.video.icefilms/plugin.video.icefilms-1.23.0.zip",
    "https://github.com/DJZONEHOUSERADIO/djzone.house.radio/archive/master.zip",
  ]

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

  tree = etree.parse(os.path.join(src, 'addon.xml'))
  tree.getroot().get('version')

  name_zip = '%s-%s.zip' % (os.path.basename(dest), tree.getroot().get('version'))
  name_zip = os.path.join(dest, name_zip)
  print name_zip
  make_zipfile(name_zip, src)

  print "Get ", os.listdir(dest)

def import_addons (list):
  for l in list:
    if not download_addon(l):
      print 'Request failed! Second try...'
      download_addon(l)

def download_addon(l):
  print 'Get: %s' % l
  try:
    r = requests.get(l, timeout=30, headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0'})
    rh = r.headers.get('content-disposition')
    if r.status_code == 200:
      if rh:
        f_name = os.path.join(tmp_path, rh.split('filename=')[1])
      else:
        f_name = os.path.join(tmp_path, l.split('/')[-1])
      print "Download: ", f_name
      with open(f_name, "wb") as code:
        code.write(r.content)
    return True
  except:
    return False

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
