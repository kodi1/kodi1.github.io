import urllib2

class GPHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
	http_error_301 = http_error_303 = http_error_307 = http_error_302