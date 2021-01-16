from os import listdir
from os.path import isfile, join
import socketserver
from urllib.parse import unquote


from config import config
from log import log


class Application(socketserver.BaseRequestHandler):
	def handle(self):
		self.data = self.request.recv(config('bufferSize')).strip()
		log(f'From: {self.client_address[0]}\n{self.data}\n\n')
		getAction = unquote(self.data.decode('utf-8')
				.split('\r\n')[0]
				.replace(' HTTP/1.1', '')
				.lstrip('GET /')
				.lower())
		if getAction == '':
			self.__rspText(self.__htLi(
					[self.__htA(l) for l in listdir(config('root'))]))
		elif '.mp4' in getAction:
			file = join(config('root'), getAction)
			self.__rspMp4(file)
		else:
			file = join(config('root'), getAction)
			self.__rspFile(file)

	def __htA(self, text):
		return f'<a href="{text}">{text}</a>'
	
	def __htLi(self, l):
		return f'<ul><li>'+'<li>'.join(l)+'</ul>'
	
	def __rspMp4(self, file):
		with open(file, 'rb') as f:
			self.request.send(bytes(f'HTTP/1.1 200 OK\r\n'
					f'content-type: video/mp4\r\n\r\n', 'utf-8'))
			self.request.sendall(f.read())
	
	def __rspFile(self, file):
		with open(file, 'rb') as f:
			self.request.sendfile(f)

	def __rspText(self, text):
		self.request.sendall(bytes(f'HTTP/1.1 200 OK\r\n'
				f'content-type: text/html\r\n\r\n'
				+ text, 'utf-8'))
