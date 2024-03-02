# -*- coding: utf-8 -*-
import re, sys, os.path, urllib, urllib2, cookielib, urlparse, base64
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.gongplay import GongPlay

reload(sys)
sys.setdefaultencoding('utf8')
_addon = xbmcaddon.Addon(id='plugin.video.gong.play')
_language = _addon.getLocalizedString
isApiEngine = True if _addon.getSetting('engine') == "0" else False 
gong = GongPlay(_addon)

def Categories():
	gong.update('browse', 'Categories')
	#addDir(_language(30209).encode('utf8'), gong.url_video_clips, 4)
	categories = gong.get_categories()
	for i in range(0, len(categories)):
		addDir(categories[i]['text'], categories[i]['url'], 1)
	if gong.is_loggedin == False:
		gong.login()
	if gong.is_loggedin == True:
		msg = _language(30204) + gong.expiration_date
		xbmc.executebuiltin('Notification(%s,%s,15000,%s)'%(gong.display_name, msg, gong.icon))


def Games(url = ''):
	#addDir(_language(30209).encode('utf8'), gong.url_video_clips, 4)
	if isApiEngine:
		loggedin = gong.login()
		if loggedin:
			if gong.is_payment_expired:
				xbmcgui.Dialog().ok(gong.addon_name, _language(30203) + gong.expiration_date)
		else:
			xbmcgui.Dialog().ok(gong.addon_name, _language(30205))
			
	games = gong.get_games(url)
	for i in range(0, len(games)):
		text = games[i]['text'] % _language(30210) if '%s' in games[i]['text'] else games[i]['text'] 
		addDir(text.encode('utf8'), games[i]['url'], 2, games[i]['icon'])
		
def Streams(match_url):
	xbmc.log("match_url: " + match_url)
	name = urllib.unquote_plus(params["name"])
	if isApiEngine:
		streams = gong.get_game_stream(match_url)
		addLink(name + " 1", streams[0], 3)
		addLink(name + " 2 HD", streams[1], 3)
	else:
		streams = gong.get_game_stream(match_url)
		if len(streams) == 0:
			if gong.is_loggedin == False:
				xbmcgui.Dialog().ok(gong.addon_name, _language(30205))
			else:
				if gong.is_payment_expired:
					xbmcgui.Dialog().ok(gong.addon_name, _language(30203) + gong.expiration_date)
				else:
					xbmc.executebuiltin('Notification(%s,%s,5000,%s)'%(gong.addon_name, _language(30206), gong.icon))
		else:
			addLink(name + "  SD", streams[0], 3)
			if (len(streams)) > 1:
				addLink( name + "  HD", streams[1], 3)

def Videoclips(url):
	video_clips = gong.get_video_clips(url)
	for i in range(0, len(video_clips)):
		addLink(video_clips[i]['text'], video_clips[i]['id'], 5, video_clips[i]['icon'])
	#Generate the link url for the next 20 items
	start = str(int(vbstart) + 20)
	next_page_url = base64.b64decode('aHR0cDovL20udmJveDcuY29tL3VzZXIvY2xpcHMuZG8/dXNyPWdvbmdiZyZhamF4PTEmc3RhcnQ9JXMmb3JkZXI9ZGF0ZQ==') % start
	addDir(_language(30211).encode('utf8'), next_page_url, 4, start)

def Playvboxstream(id):
	PLAY(gong.get_clip_stream(id))


def Play(url):
	li = xbmcgui.ListItem(iconImage=gong.icon, thumbnailImage=gong.icon, path=url)
	li.setInfo('video', { 'title': name })
	xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=url))

def addLink(name, url, mode, icon = ''):
	return addItem(name, url, mode, False, icon)

def addDir(name, url, mode, icon = '', vbstart = ''):
	return addItem(name, url, mode, True, icon, vbstart)

def addItem(name, url, mode, isDir, icon, vbstart = ''):
	item_icon = icon if icon != '' else gong.icon
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&vbstart="+vbstart
	ok=True
	liz=xbmcgui.ListItem(name, iconImage=item_icon, thumbnailImage=item_icon)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	liz.setProperty("IsPlayable" , "true")
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isDir)
	return ok
	
def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param

params=get_params()
url=None
name=None
iconimage=None
mode=None
vbstart = '0'

try:
	url = urllib.unquote_plus(params["url"])
except:
	pass
try:
	name = urllib.unquote_plus(params["name"])
except:
	pass
try:
	iconimage = urllib.unquote_plus(params["iconimage"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
try:
	vbstart = params["vbstart"]
except:
	pass
	
if isApiEngine == False and (mode==None or url==None or len(url) < 1):
	Categories()

elif isApiEngine and (mode==None or url==None or len(url) < 1):
	Games()
	
elif mode == 1:
	Games(url)

elif mode==2:
	Streams(url)

elif mode==3:
	Play(url)

elif mode==4:
	Videoclips(url)
	
elif mode==5:
	Playvboxstream(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
