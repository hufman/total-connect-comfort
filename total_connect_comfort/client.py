#!/usr/bin/env python3


import codecs
import json
import time
import urllib.parse
import urllib.request


PREFIX = 'https://mytotalconnectcomfort.com/'


class Client(object):
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.urlopener = urllib.request.build_opener()
		self.urlopener.addheaders = [('User-Agent', 'MyTotalConnectComfortClient/0.1')]
		self.urlopener.add_handler(urllib.request.HTTPCookieProcessor())
		self.login()

	def login(self):
		form = {
			'UserName': self.username,
			'Password': self.password,
			'RememberMe': 'false'
		}
		headers = {
			'Origin': PREFIX + 'portal',
		}
		data = urllib.parse.urlencode(form).encode('utf-8')
		request = urllib.request.Request(PREFIX + 'portal', data, headers)
		self.urlopener.open(PREFIX + 'portal')	# get signin cookie
		data = self.urlopener.open(request)	# actually sign in
		if '/portal/Account/LogOff' in data.read().decode():
			# successful login
			pass
		else:
			raise ValueError("Invalid credentials")

	def _request(self, path, data={}, headers={}):
		if isinstance(data, str):
			data = data.encode('utf-8')
		elif isinstance(data, bytes):
			data = data
		elif data != {}:
			data = json.dumps(data).encode('utf-8')
		else:
			data = None
		headers = dict(headers)
		headers['X-Requested-With'] = 'XMLHttpRequest'
		headers['Accept'] = 'application/json, text/javascript'
		if data != None:
			headers['Content-Type'] = 'application/json; charset=utf-8'
		request = urllib.request.Request(PREFIX + path, data, headers)
		return self.urlopener.open(request)	# actually fetch

	def _request_data(self, path, data={}, headers={}):
		data = self._request(path, data, headers)
		reader = codecs.getreader(data.headers.get_content_charset())
		return reader(data)

	def locations(self):
		path = 'portal/Location/GetLocationListData?page=1&filter='
		data = self._request_data(path, '')
		return json.load(data)
		
	def location_overview(self, locationId):
		path = 'portal/Device/GetZoneListData?locationId=%s&page=1' % (locationId,)
		data = self._request_data(path, '')
		return json.load(data)

	def device_status(self, device_id):
		utc_seconds = time.mktime(time.gmtime())
		path = 'portal/Device/CheckDataSession/%s?_=%s' % (device_id, utc_seconds)
		data = self._request_data(path)
		return json.load(data)

if __name__ == '__main__':
	client = Client('email@gmail.com', 'password')
	pp = lambda data: json.dumps(data, sort_keys=True,indent=4,separators=(',', ': '))
	print(pp(client.locations()))
	#print(pp(client.location_overview(1747926)))
	#print(pp(client.device_status(1942775)))
