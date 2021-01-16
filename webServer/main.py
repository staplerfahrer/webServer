import sys
import socketserver

from config import config
from application import Application
from log import log


if __name__ == '__main__':
	with socketserver.TCPServer(
			(config('address'), config('port')), 
			Application) as srv:
		srv.serve_forever()
