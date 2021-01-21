from functools import reduce
from os import listdir
from os.path import isfile, isdir, join, sep, normpath, relpath, dirname, split


class HandlerCollection():
	def __init__(self, get, send, sendall, sendfile, toClientPath):
		self._get = get
		self._send = send
		self._sendall = sendall
		self._sendfile = sendfile
		self._toClientPath = toClientPath

	def h000index(self):
		if not isdir(self._get):
			return False
		entries = [normpath(self._get + sep + f) 
				for f in listdir(self._get)]
		links = [self.__htmlA(self._toClientPath(l)) for l in entries]
		self.__rspUtf8(self.__htmlLi(links))
		return True

	def h001supported(self):
		if not isfile(self._get):
			return False
		mimes = [
			('mp4', 'video/mp4'),
			('bmp', 'image/bmp'),
			('gif', 'image/gif'),
			('jpg', 'image/jpeg'),
			('jpeg', 'image/jpeg'),
			('png', 'image/png'),
			('apng', 'image/png'),
			('mp2t', 'video/mp2t'),
			('ts', 'video/mp2t'),
			('mp3', 'audio/mpeg'),
			('mp4', 'video/mp4'),
			('mpg', 'video/mpeg'),
			('mpeg', 'video/mpeg'),
			('ogg', 'audio/ogg'),
			('oga', 'audio/ogg'),
			('ogv', 'video/ogg'),
			('wav', 'audio/wav'),
			('weba', 'audio/webm'),
			('webm', 'video/webm'),
			('webp', 'image/webp')
		]
		mime = reduce(lambda m, x: x[1] if self._get.endswith(x[0]) else m, mimes, '')
		if not mime:
			return False
		with open(self._get, 'rb') as f:
			self._send(bytes(f'HTTP/1.1 200 OK\r\n'
					f'content-type: {mime}\r\n\r\n', 'utf-8'))
			self._sendall(f.read())
		return True
	
	def h002raw(self):
		if not isfile(self._get):
			return False
		with open(self._get, 'rb') as f:
			self._sendfile(f)
		return True

	def h999four04(self):
		self.__rspUtf8('Resource not found.', '404 Not Found')
		return True

	def __htmlA(self, path):
		return f'<a href="/{path}">{split(path)[1]}</a>'
	
	def __htmlLi(self, l):
		return f'<ul><li>'+'<li>'.join(l)+'</ul>'
	
	def __rspUtf8(self, text, code='200 OK'):
		self._sendall(bytes(f'HTTP/1.1 {code}\r\n'
				f'content-type: text/html; charset=utf-8\r\n\r\n'
				+ text, 'utf-8'))
