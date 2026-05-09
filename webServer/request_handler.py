#TODO: create a class with config as a dictionary, methods for serving index and files, method for getting mime types, put thumbnail generation back in
from urllib.parse import unquote
import os
import subprocess

import filesystem as fs
import handle_directory
import handle_thumbnail
from log import log
from config import config


def build_response(req: str) -> bytes:
	req, rangeL, rangeU = _decode_request(req)
	reqServerPath       = fs.to_server_path(req)
	end                 = None

	if req == '/favicon.ico':
		log('favicon.ico')
		data, mime = fs.read_file_bytes('resources/favicon.png')[0], 'image/png'
	elif req == '/favicon.svg':
		log('favicon.svg')
		data, mime = fs.read_file_bytes('resources/favicon.svg')[0], 'image/svg+xml'
	elif os.path.isdir(reqServerPath):
		data, mime = handle_directory.run(reqServerPath)
	elif reqServerPath.endswith('?tn') \
			and fs.is_picture(reqServerPath[:-3]): # remove ?tn
		data, mime = handle_thumbnail.run(reqServerPath)
	elif reqServerPath.endswith('?del'):
		log('__deleteFile')
		data, mime = fs.delete_file(reqServerPath)
	elif reqServerPath.endswith('?explorer'):
		log('__openExplorer')
		data, mime = _open_explorer(reqServerPath)
	elif (not os.path.isfile(reqServerPath)) \
			or (not fs.is_picture(reqServerPath)):
		log(f'404 {reqServerPath} not isfile(): {not os.path.isfile(reqServerPath)} or not fs.isPicture(): {not fs.is_picture(reqServerPath)}')
		return b'HTTP/1.1 404 Not Found\r\ncontent-type: text/plain\r\ncontent-length: 9\r\n\r\nNot Found'
	else:
		data, mime, rangeL, rangeU, end = fs.serve_file(reqServerPath, rangeL, rangeU)

	return _encode(data, mime, rangeL, rangeU, end)


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

	reqHttpGet = unquote(reqHttpGet[4:-9])

	rangeLower = None
	rangeUpper = None
	if reqRange:
		reqRange = str.replace(reqRange[0].lower(), 'range: bytes=', '')
		rangeSplit = reqRange.split('-')
		rangeLower = int(rangeSplit[0] or '0')
		rangeUpper = int(rangeSplit[1]) if rangeSplit[1] != '' else None # 0-based, inclusive

	return reqHttpGet, rangeLower, rangeUpper


def _encode(data: bytes, mime: str, rangeL: int | None, rangeU: int | None, end: int | None) -> bytes:
	if rangeL is not None and rangeU is not None and end is not None:
		return bytes(
			f'HTTP/1.1 206 Partial Content\r\n'
			f'Accept-Ranges: bytes\r\n'
			f'content-type: {mime}\r\n'
			f'content-length: {len(data)}\r\n'
			f'cache-control: max-age={config("cacheSeconds")}\r\n'
			f'content-range: bytes {rangeL}-{rangeU}/{end}\r\n\r\n', 'utf-8') + data
	return bytes(
		f'HTTP/1.1 200 OK\r\n'
		f'Accept-Ranges: bytes\r\n'
		f'content-type: {mime}\r\n'
		f'content-length: {len(data)}\r\n'
		f'cache-control: max-age={config("cacheSeconds")}\r\n\r\n', 'utf-8') + data

