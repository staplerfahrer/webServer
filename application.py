import re
import socketserver
from os.path import normpath, relpath, sep
from urllib.parse import unquote

from config import config
from handlerCollection import HandlerCollection
from log import log


class Application(socketserver.BaseRequestHandler):
	def __init__(self, request, client_address, server):
		super().__init__(request, client_address, server)

	def handle(self):
		self.req = self.request.recv(config('bufferSize')) \
				.decode('utf-8').strip()
		self.reqGet = self.__getWhat()

		log(f'From: {self.client_address[0]}\n{self.req}\n\n')

		handlers = HandlerCollection(self.reqGet, self.request.send, 
				self.request.sendall, self.request.sendfile, 
				self.__toClientPath)
		for handler in [getattr(handlers, h) 
				for h in dir(handlers) if not h.startswith('_')]:
			if handler():
				break

	def __getWhat(self):
		line1 = self.req.split('\r\n')[0]
		request = unquote(re.sub(r'(^GET | HTTP/1.1$|\.\.)', '', line1))
		return self.__toServerPath(request)

	def __toServerPath(self, reqPath):
		return normpath(config('root') + reqPath)

	def __toClientPath(self, absPath):
		return relpath(absPath, config('root')).replace(sep, '/')
