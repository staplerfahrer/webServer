import sys
import socket 
import socketserver

from config import config
from application import Application
from log import log


if __name__ == '__main__':
	hostName = socket.gethostname() 
	hostIp = socket.gethostbyname(hostName)
	log(f'Hostname: {hostName}, host IP: {hostIp}, '
			f'serving on {config("address")}:{config("port")}') 
	log('Serves only one request at a time. Single-threaded, synchronous.')
	with socketserver.TCPServer(
			(config('address'), config('port')), 
			Application) as srv:
		srv.serve_forever()
