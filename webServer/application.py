from os import listdir
from os.path import isfile, isdir, join, sep, normpath, relpath, dirname, split
import re
import socketserver
from urllib.parse import unquote

from config import config
from log import log


class Application(socketserver.BaseRequestHandler):
	def __init__(self, request, client_address, server):
		self.handlers = [
			self.__index, 
			self.__mp4, 
			self.__mkv, 
			self.__raw, 
			self.__404]
		super().__init__(request, client_address, server)

	def __getResource(self):
		line1 = self.req.split('\r\n')[0]
		request = unquote(re.sub(r'(^GET | HTTP/1.1$|\.\.)', '', line1))
		return self.__toServerPath(request)

	def handle(self):
		self.req = self.request.recv(config('bufferSize')) \
				.decode('utf-8').strip()
		self.reqGet = self.__getResource()

		log(f'From: {self.client_address[0]}\n{self.req}\n\n')

		for handler in self.handlers:
			if handler():
				break

	def __index(self):
		if not isdir(self.reqGet):
			return False
		#just use back button for [dirname(self.reqGet)] + 
		entries = [normpath(self.reqGet + sep + f) 
				for f in listdir(self.reqGet)]
		links = [self.__htmlA(self.__toClientPath(l)) for l in entries]
		self.__rspText(self.__htmlLi(links))
		return True

	def __mp4(self):
		if not self.reqGet.endswith('.mp4') or not isfile(self.reqGet):
			return False
		with open(self.reqGet, 'rb') as f:
			self.request.send(bytes(f'HTTP/1.1 200 OK\r\n'
					f'content-type: video/mp4\r\n\r\n', 'utf-8'))
			self.request.sendall(f.read())
		return True

	def __mkv(self):
		if not self.reqGet.endswith('.mkv')	or not isfile(self.reqGet):
			return False
		with open(self.reqGet, 'rb') as f:
			self.request.send(bytes(f'HTTP/1.1 200 OK\r\n'
					f'content-type: video/x-matroska\r\n\r\n', 'utf-8'))
			self.request.sendall(f.read())
		return True
	
	def __raw(self):
		if not isfile(self.reqGet):
			return False
		with open(self.reqGet, 'rb') as f:
			self.request.sendfile(f)
		return True

	def __404(self):
		self.__rspText('Resource not found.', '404 Not Found')
		return True

	def __toServerPath(self, reqPath):
		return normpath(config('root') + reqPath)

	def __toClientPath(self, absPath):
		return relpath(absPath, config('root')).replace(sep, '/')

	def __htmlA(self, path):
		return f'<a href="/{path}">{split(path)[1]}</a>'
	
	def __htmlLi(self, l):
		return f'<ul><li>'+'<li>'.join(l)+'</ul>'
	
	def __rspText(self, text, code='200 OK'):
		self.request.sendall(bytes(f'HTTP/1.1 {code}\r\n'
				f'content-type: text/html\r\n\r\n'
				+ text, 'utf-8'))
