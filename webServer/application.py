import re
import socketserver
from os.path import normpath, relpath, sep, getsize
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
		requestedResource = unquote(re.sub(r'(^GET | HTTP/1.1$|\.\.)', '', line1))
		rangeHdr = ([l for l in self.req.split('\r\n') 
				if 'range' in l.lower()]+[None])[0]
		return {
			'resource': self.__toServerPath(requestedResource),
			'range': self.__toRange(rangeHdr)}

	def __toServerPath(self, requestedResource):
		return normpath(config('root') + requestedResource)

	def __toClientPath(self, absPath):
		return relpath(absPath, config('root')).replace(sep, '/')

	def __toRange(self, rangeHeader):
		# An HTTP/1.1 feature.
		# https://httpwg.org/specs/rfc7233.html
		if not rangeHeader:
			return None
		if not 'bytes=' in rangeHeader:
			return None
		byteses = [int(x) for x in re.findall(r'(\d+)', rangeHeader)]
		if not len(byteses):
			return None
		return (byteses[0], 
				byteses[1] # inclusive
				if len(byteses) > 1 
				else None)