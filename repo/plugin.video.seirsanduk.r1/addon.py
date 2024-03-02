# -*- coding: utf-8 -*-
import urllib
from re import compile as Compile
from xbmc import log
from xbmcgui import Dialog
from xbmcswift2 import Plugin

BASE=['https://www.glebul.com/']


header='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/59.0'

plugin=Plugin()

opener=urllib.request.build_opener(urllib.request.HTTPHandler,urllib.request.HTTPRedirectHandler())
urllib.request.install_opener(opener)

@plugin.route('/')
def index():
    log('path: [/]')
    items=[]
    for B in BASE:
        try:
            source=openUrl(B)
        except:
            source=None
        match=Compile('<a href="(.+?)"><img src="(.+?)".*>(.+?)<\/a').findall(source)
        if not match:
            continue
        break
    items=[{'label':name,'thumbnail':B+thumbnail,'path':plugin.url_for('index_source',url=url,name=name,icon=B+thumbnail)} for url,thumbnail,name in match]
    return plugin.finish(items)
 
@plugin.route('/stream/<url>/<name>/<icon>/')
def index_source(url,name,icon):
    log('path: [/stream/'+url+'/'+name+'/'+icon+']')
    log('url:'+url)
    source=openUrl(url)
    match=Compile('file:"(.+?)"').findall(source)
    item={'label':name,'path':match[0]}
    plugin.play_video(item)
    Dialog().notification(name,'',icon,8000,sound=False)
    return plugin.finish(None,succeeded=False)
   
def openUrl(url):
    req=urllib.request.Request(url)
    req.add_header('User-Agent',header)
    response=urllib.request.urlopen(req)
    source=response.read().decode('utf-8')
    response.close()
    return source

if __name__ == '__main__':
    plugin.run()