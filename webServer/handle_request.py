from urllib.parse import unquote
import os
import subprocess

import filesystem as fs
import handle_directory
import handle_thumbnail
from log import log
from config import config


def build_response_bytes(req: str) -> bytes:
	req, range_l, range_u = _decode_request(req)
	req_server_path       = fs.to_server_path(req)
	end                   = None

	if req == '/favicon.ico' or req == '/favicon.svg':
		data, mime = fs.read_file_bytes('resources/favicon.svg')[0], 'image/svg+xml'
	elif req.startswith('/.well-known'):
		data, mime = b'', 'text/plain'
	elif req == '/thumbnail-placeholder.png':
		data, mime = fs.read_file_bytes('resources/thumbnail-placeholder.png')[0], 'image/png'
	elif os.path.isdir(req_server_path):
		data, mime = handle_directory.run(req_server_path)
	elif req_server_path.endswith('?tn') \
			and fs.is_picture(req_server_path[:-3]): # remove ?tn
		data, mime = handle_thumbnail.run(req_server_path)
	elif req_server_path.endswith('?del'):
		data, mime = fs.delete_file(req_server_path)
	elif req_server_path.endswith('?explorer'):
		data, mime = _open_explorer(req_server_path)
	elif (not os.path.isfile(req_server_path)) \
			or (not fs.is_picture(req_server_path)):
		log(f'404 {req_server_path} not isfile(): {not os.path.isfile(req_server_path)} or not fs.isPicture(): {not fs.is_picture(req_server_path)}')
		return b'HTTP/1.1 404 Not Found\r\ncontent-type: text/plain\r\ncontent-length: 9\r\n\r\nNot Found'
	else:
		data, mime, range_l, range_u, end = fs.serve_file(req_server_path, range_l, range_u)

	return _encode(data, mime, range_l, range_u, end)


def _open_explorer(serverPath: str) -> tuple[bytes, str]:
	target = serverPath[:-9] # strip '?explorer'
	log('exploring: ' + target)
	subprocess.Popen(f'explorer /select,"{target}"', shell=True)
	return b'ok', 'text/plain'


def _decode_request(req: str) -> tuple[str, int | None, int | None]:
	# req is the WHOLE http request
	requestLines = req.split('\r\n')
	reqHttpGet = requestLines[0]
	reqRange   = [l for l in requestLines if 'range:' in str.lower(l)]

	if not reqHttpGet.startswith('GET '):
		raise Exception('request not GET')
	if not reqHttpGet.endswith(' HTTP/1.1'):
		raise Exception('request not HTTP/1.1')

	reqHttpGet = unquote(reqHttpGet[4:-9], encoding='utf-8', errors='strict')

	rangeLower = None
	rangeUpper = None
	if reqRange:
		reqRange = str.replace(reqRange[0].lower(), 'range: bytes=', '')
		rangeSplit = reqRange.split('-')
		rangeLower = int(rangeSplit[0] or '0')
		rangeUpper = int(rangeSplit[1]) if rangeSplit[1] != '' else None # 0-based, inclusive

	return reqHttpGet, rangeLower, rangeUpper


def _encode(data: bytes, mime: str, range_l: int | None, range_u: int | None, end: int | None) -> bytes:
	if range_l is not None and range_u is not None and end is not None:
		return bytes(
			f'HTTP/1.1 206 Partial Content\r\n'
			f'Accept-Ranges: bytes\r\n'
			f'content-type: {mime}\r\n'
			f'content-length: {len(data)}\r\n'
			f'cache-control: max-age={config("cacheSeconds")}\r\n'
			f'content-range: bytes {range_l}-{range_u}/{end}\r\n\r\n', 'utf-8') + data
	return bytes(
		f'HTTP/1.1 200 OK\r\n'
		f'Accept-Ranges: bytes\r\n'
		f'content-type: {mime}\r\n'
		f'content-length: {len(data)}\r\n'
		f'cache-control: max-age={config("cacheSeconds")}\r\n\r\n', 'utf-8') + data

