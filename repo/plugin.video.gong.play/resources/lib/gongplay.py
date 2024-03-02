import xbmc, xbmcaddon, urllib, urllib2, cookielib, urlparse, os.path, sys, re, hashlib, time, json, gzip, base64
from StringIO import StringIO
from redirecthandler import GPHTTPRedirectHandler
from ga import ga

reload(sys)  
sys.setdefaultencoding('utf8')

class GongPlay:

	display_name = ''
	debug = True
	is_loggedin = False
	is_payment_expired = True
	expiration_date = ''
	subscription_expired_msg = ''
	subscription_msg = ''
	game_title = ''
	addon_name = ''
	addon_id = ''
	username = ''
	password = ''
	debug = False
	cj = cookielib.LWPCookieJar()
	cookie_file = ''
	cookie_file_vbox = ''
	icon = ''
	#urls
	url_main = base64.b64decode('aHR0cDovL3BsYXkuZ29uZy5iZy8=')
	url_login = base64.b64decode('aHR0cDovL3BsYXkuZ29uZy5iZy9zaWduaW4=')
	url_fixtures = base64.b64decode('aHR0cDovL3BsYXkuZ29uZy5iZy9maXh0dXJl')
	url_playapi = base64.b64decode('aHR0cDovL3BsYXlhcGkuZ29uZy5iZy9hcGkvZml4dHVyZXM/aGFzaD0=')
	url_playlogin = base64.b64decode('aHR0cDovL3BsYXlhcGkuZ29uZy5iZy9hcGkvc2lnbmluP2hhc2g9')
	url_video_clips = base64.b64decode('aHR0cDovL3Zib3g3LmNvbS91c2VyOmdvbmdiZz9wPWFsbHZpZGVvcw==')
	url_vbox_resolver = base64.b64decode('aHR0cDovL3Zib3g3LmNvbS9ldGMvZXh0LmRvP2tleT0=')
	api_hash = ''
	#session_id = ''
	#User agents
	user_agent = ''
	ua_mobile = 'Mozilla/5.0 (Linux; Android 5.0.2; bg-bg; SAMSUNG GT-I9195 Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Version/1.0 Chrome/18.0.1025.308 Mobile Safari/535.19' 
	ua_pc = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
	last_response = ''
	isApiEngine = True
	
	def __init__(self, addon):
		self.addon_name = addon.getAddonInfo('name')
		self.addon_id = addon.getAddonInfo('id')
		self.version = addon.getAddonInfo('version')
		self.icon = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), "icon.png"))
		self.username = addon.getSetting('username')
		self.password = addon.getSetting('password')
		self.isApiEngine = True if addon.getSetting('engine') == "0" else False 
		self.debug = True if addon.getSetting('debug') == 'true' else False
		xbmc.log("plugin.video.gong.play | debugging log is set to " + str(self.debug))
		self.api_hash = self.hash1()
		self.user_agent = self.ua_mobile
		if self.isApiEngine:
			self.url_playapi = self.url_playapi + self.api_hash
			self.url_login = self.url_playlogin + self.api_hash
			self.user_agent = 'okhttp/2.3.0'
		profile = xbmc.translatePath( addon.getAddonInfo('profile'))
		self.cookie_file = os.path.join(profile, '.cookies')
		self.cookie_file_vbox = os.path.join(profile, '.vboxcookie')
		cookieprocessor = urllib2.HTTPCookieProcessor(self.cj)
		opener = urllib2.build_opener(GPHTTPRedirectHandler, cookieprocessor)
		urllib2.install_opener(opener)

	def request(self, url, ua = user_agent, rf = url_main):
		if os.path.isfile(self.cookie_file):
			self.cj.load(self.cookie_file)
		req = urllib2.Request(url)
		req.add_header('User-Agent', ua)
		req.add_header('Referer', rf)
		req.add_header('Accept', '*/*')
		req.add_header('Accept-Encoding', 'gzip')
		res = urllib2.urlopen(req)
		self.last_response = self.parse_gzip(res)
		if self.debug: xbmc.log("plugin.video.gong.play | Received response for URL:" + url + "\r\n" + self.last_response)
		res.close()
		if not 'vbox7' in url and self.isApiEngine == False:
			self.isLoggedIn()
	
	def parse_gzip(self, res):
		if res.info().get('Content-Encoding') == 'gzip':
		    buf = StringIO(res.read())
		    f = gzip.GzipFile(fileobj = buf)
		    return f.read()
		else:
			return res.read()
			
	def login(self):
		post_data = urllib.urlencode({'email' : self.username, 'password' : self.password})
		xbmc.log(post_data)
		req = urllib2.Request(self.url_login, post_data)
		req.add_header('User-Agent', self.user_agent)
		req.add_header('Content-Type', "application/x-www-form-urlencoded; charset=UTF-8")
		req.add_header('Accept-Encoding', 'gzip')
		res = urllib2.urlopen(req)
		self.last_response = self.parse_gzip(res)
		res.close()
		
		if not os.path.exists(os.path.dirname(self.cookie_file)):
			try:
				os.makedirs(os.path.dirname(self.cookie_file))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST: pass
		self.cj.save(self.cookie_file, ignore_discard=True)
		return self.isLoggedIn()
		
	def isLoggedIn(self):

		if self.isApiEngine:
			json_response = json.loads(self.last_response)
			reg_status = json_response['reg_status'][0]
			#validto element exists only when login is successful
			try:
				self.expiration_date =  reg_status['validto'] #'2015-11-17 18:43:09'
				validTo = re.sub('[^\d]', '', self.expiration_date)
				now = time.strftime("%Y%m%d%H%M00")
				self.is_payment_expired = True if validTo <= now else False
				#self.session_id = reg_status['session_id']
				self.is_loggedin = True
			except Exception as ex:
				xbmc.log("| %s | %s | %s" % (self.addon_id, type(ex).__name__, str(ex)))
				self.is_loggedin =  False
		else:
			user_div = re.compile('user-info["\'\s]>(.*?)</div', re.DOTALL).findall(self.last_response)
			if (len(user_div)) > 0:
				matches = re.compile('(/signout["\'\s]{1})').findall(user_div[0])
				self.is_loggedin = True if len(matches) > 0 else False
				self.get_display_name(user_div[0])
				self.get_payment_info(user_div[0])
				self.is_loggedin = True
		return self.is_loggedin

	def get_display_name(self, text):
		matches = re.compile('user-name.*>(.*?)</a').findall(text)
		if len(matches) > 0:
			self.display_name = matches[0]
			
	def get_payment_info(self, text):
		navbar = re.compile('navbar-right.*"\s*>(.*?)<').findall(text)
		if (len(navbar)) > 0 :
			self.subscription_msg = navbar[0]
			date = re.compile('([0-9]{1,2}.*[0-9]{4}.*[0-9:]{5})').findall(navbar[0])
			if (len(date)) > 0:
				self.expiration_date = date[0]
		expired = re.compile('alert-abonament').findall(text)
		self.is_payment_expired = True if len(expired) > 0 else False
		
	def get_categories(self):
		categories = []
		self.request(self.url_fixtures)
		matches = self.find_regex('ul.+program-nav.+tablist[\s"\']+>(.*?)</ul', re.DOTALL)
		
		if len(matches) != 0:
			#Find out category links and titles. 
			hrefs = re.compile('href[\s="\']*(.*?)["\'\s]+aria').findall(matches[0])
			if self.debug: xbmc.log(self.addon_id + " | get_categories | Found " + str(len(hrefs)) + " matches for regex 'href[\s=\"\']*(.*?)[\"\'\s]+aria'")
			names = re.compile('p.+?>(.*?)</p').findall(matches[0])
			if self.debug: xbmc.log(self.addon_id + " | get_categories | Found " + str(len(names)) + " matches for regex 'p.+?>(.*?)</p'")
			# The hrefs are always one more than the category names
			if len(names) == len(hrefs) - 1:
				categories.append({'text' : 'Програма - Всички категории', 'url' : hrefs[0]})
				for i in range(0, len(names)):
					#Filter category and capitalize it
					title = names[i][0].upper() + names[i][1:]
					category = {}
					category['text'] = title.replace('<br>', '')
					category['url'] =  urlparse.urljoin(self.url_main, hrefs[i+1])
					categories.append(category)

		return categories

	def get_games(self, url):
		games = []
		self.request(self.url_playapi)

		if self.isApiEngine:
			json_response = json.loads(self.last_response)
			epg = json_response['epg']
			for i in range(0, len(epg)):
				teams = epg[i]["home_name"] + " - " + epg[i]["away_name"]
				title  = "| [COLOR white]" + teams + "[/COLOR]"
				if self.is_game_started(epg[i]['showstart']):
					live = "[COLOR green][B]%s[/B][/COLOR]"
					title = "[COLOR white]" + live + " " + teams + "[/COLOR]"	
				game = {}
				game['url'] = epg[i]["show_id"]
				game['text'] = "[B]" + epg[i]["showstart"][:16] + "[/B] " + title
				game['icon'] = epg[i]['portrait']
				games.append(game)
		else:
			self.request(self.url_fixtures)
			dates = self.find_regex('date-info[\s\'"]+.*>(.*?)</')
			hours = self.find_regex('time-info[\s\'"]+.*>(.*?)</')
			details = self.find_regex('href[\s="\']+(.*)"\s+.*title[\s=\'"]+(.*)"\s+.*class[=\s"\']+.*btn-table.*(regular|live)')
			if len(dates) == len(hours) and len(hours) == len(details):
				for i in range(0, len(dates)):
					title = "| [COLOR white]" + details[i][1] + "[/COLOR]"
					if details[i][2].lower() == "live":
						live = "[COLOR green][B]%s[/B][/COLOR]" 
						title = "[COLOR white]" + live + " " + details[i][1] + "[/COLOR]"
					game = {}
					game['url'] = urlparse.urljoin(self.url_main, urllib.quote(details[i][0]))
					game['text'] = '[B]' + dates[i][:9] + " " + hours[i] + "[/B] " + title
					game['icon'] = ''
					games.append(game)
					
			if self.debug : xbmc.log(self.addon_id + " | get_games | Found " + str(len(games)) + " games on " + url)
		return games
	
	
	def is_game_started(self, datetime):
		# strip anything that's not a digital "2015-11-02 17:30:00"
		showstart = re.sub('[^\d]', '', datetime)
		now = time.strftime("%Y%m%d%H%M00")
		return True if showstart <= now else False
		
	def get_game_stream(self, url_game):
		#streams = ["http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8"]
		streams = []
		
		if self.isApiEngine:
			stream = self.get_mobile_streams(url_game, 'stream_android')
			streams.append(stream)
			stream = self.get_mobile_streams(url_game, 'stream_iphone')
			streams.append(stream)
		else:
			if self.is_loggedin == False:
				self.login()
			self.request(url_game)

			matches = self.find_regex('iframe.+src[="\'\s]+(.*cdn.*?)[\'"\s]+')
			if len(matches) > 0:
				if self.debug : xbmc.log(self.addon_id + " | Found Iframe url=" + matches[0])
				url_iframe = matches[0]
				self.request(matches[0])
				video = self.find_regex('video.+src[="\']+(.*?)[\'"\s]+')
				if len(video) > 0:
					xbmc.log(self.addon_id + " | get_game_stream | Found video url=" + video[0])
					streams.append(video[0])
					streams.append(re.sub('_(1)\.s', "_2.s", video[0]))
				
		return streams
	
	def get_mobile_streams(self, show_id, type):
		try:
			session_id = ''
			with open(self.cookie_file, 'r') as c: data = c.read()
			match = re.compile('PHPSESSID=(.*?);').findall(data)
			if len(match) > 0:
				session_id = match[0]
				
			self.request(base64.b64decode("aHR0cDovL3BsYXlhcGkuZ29uZy5iZy9hcGkvbWF0Y2gv") + show_id + '/' + session_id + '?hash=' + self.api_hash)
			json_response = json.loads(self.last_response)
			reg_status = json_response['reg_status'][0]
			stream = reg_status[type] + self.hash2()
			xbmc.log(self.addon_id + " | get_mobile_streams(show_id="+show_id+", type="+type+") | Found stream url=" + stream)
		except Exception:
			stream = ''
			
		return stream
		
		
	def find_regex(self, exp, flags=re.IGNORECASE):
		matches = re.compile(exp, flags).findall(self.last_response)
		if self.debug: xbmc.log(self.addon_id + " | find_regex | Found " + str(len(matches)) + " matches for regex '" + exp + "', flags=" + str(flags))
		return matches
		
	def get_video_clips(self, url):
		self.request(url, self.ua_mobile, '')
		video_clips = []
		thumbs = re.compile('video-thumb(.*?)</div', re.DOTALL).findall(self.last_response)
		titles = re.compile('video-info-title.*?>(.*?)</a',  re.DOTALL).findall(self.last_response)
		
		#matches = self.find_regex('a.*href=\"/play:([0-9a-zA-Z]{10})\".*img.*src=\"(.*?)\".*alt=\"(.*?)\"')
		if len(thumbs) > 0 and len(thumbs) == len(titles):
			for i in range(0, len(thumbs)):
				href = re.compile('href[=\s\'"]+/play:(.*?)[\s\'"]+', re.DOTALL).findall(thumbs[i])
				img = re.compile('img.*?src[=\s\'"]+(.*?)[\s\'"]+', re.DOTALL).findall(thumbs[i])
				duration = re.compile('vt-duration[\'"]+.*?>(.*?)</', re.DOTALL).findall(thumbs[i])
				
				
				video_clip = {}
				video_clip['id'] = href[0]
				video_clip['icon'] = img[0]
				video_clip['text'] = titles[i] + " (" + duration[0] + ")"
				video_clips.append(video_clip)
				
		return video_clips
	
	def get_clip_stream(self, id):
		self.request(self.url_vbox_resolver + id, self.ua_pc, self.url_video_clips)
		matches = self.find_regex('flv_addr=(.*?)&')
		return matches[0] if len(matches) > 0 else ''
	
	
	def hash1(self):
		m = hashlib.md5()
		pwd = base64.b64decode("JTAjNEwzNjlwY2JNSHRsYzlFblpQR25XdSNNUzZIMiM=")
		m.update(pwd + time.strftime("%Y%m%d"))
		return m.hexdigest()
	
	def hash2(self):
		m = hashlib.md5()
		pwd = base64.b64decode("JHJzZHcuLnRmZWV3M0AzMzNsOzQt")
		m.update(pwd + self.get_ip() + '-' + time.strftime("%d.%m.%Y"))
		return m.hexdigest()
	
	def get_ip(self):
		url = base64.b64decode('aHR0cDovL2dvbmcuc21hcnR4bWVkaWEuZXUvaXAucGhw')
		self.request(url)
		json_response = json.loads(self.last_response)
		geo_ip = json_response['geo_ip'][0]
		ip = geo_ip['ip']
		return ip
		
	def update(self, name, location, crash=None):
		p = {}
		p['an'] = self.addon_name
		p['av'] = self.version
		p['ec'] = 'Addon actions'
		p['ea'] = name
		p['ev'] = '1'
		p['ul'] = xbmc.getLanguage()
		p['cd'] = location
		ga('UA-79422131-3').update(p, crash)