import os
import traceback
import urllib.parse as urlparse

from config import config
from log import log

MIME: dict[str, str] = {
	'.jpg' : 'image/jpeg',
	'.jpeg': 'image/jpeg',
	'.png' : 'image/png',
	'.gif' : 'image/gif',
	'.webp': 'image/webp',
	'.bmp' : 'image/bmp',
	'.svg' : 'image/svg+xml',
	'.mp4' : 'video/mp4',
	'.m4v' : 'video/mp4',
	'.mov' : 'video/mp4',
	'.ts'  : 'video/mp2t',
	'.webm': 'video/webm',
	'.mp3' : 'audio/mpeg',
	'.m4a' : 'audio/mp4',
	'.ogg' : 'audio/ogg',
	'.wav' : 'audio/wav',
}


def to_client_path(file_path: str) -> str:
	url = file_path.replace(config('root'), '').replace('\\', '/')
	return urlparse.quote(url) if url else '/'


def to_server_path(url: str) -> str:
	return config('root') + url.replace('/', '\\')


def read_file_bytes(file_name: str, range_l: int | None = None, range_u: int | None = None) \
	 	-> tuple[bytes, int | None, int | None, int | None]:
	try:
		with open(file_name, 'rb') as f:
			if range_l is not None:
				f.seek(0, os.SEEK_END)
				end = f.tell()

				if range_l > end:
					return bytes(), end - 1, end - 1, end - 1

				# range_u may be None
				# (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Range)
				if range_u is None or range_u >= end:
					range_u = end - 1
				f.seek(range_l)
				return f.read(range_u - range_l + 1), range_l, range_u, end
			return f.read(), None, None, None
	except:
		log(f'Exception at "__readFileBytes": {traceback.format_exc()}')
		return b'', None, None, None


def delete_file(server_path: str) -> tuple[bytes, str]:
	if not config('allowDelete'):
		return b'disabled', 'text/plain'
	try:
		target = server_path[:-4]
		os.rename(target, target + '.deleted')
		return b'ok', 'text/plain'
	except:
		log(f'Exception at delete: {traceback.format_exc()}')
		return b'error', 'text/plain'


def is_picture(file_name: str) -> bool:
	parts = os.path.splitext(file_name)
	return parts[1].lower() in MIME


def serve_file(server_path: str, range_l: int | None, range_u: int | None) \
		-> tuple[bytes, str, int | None, int | None, int | None]:
	mime = MIME[os.path.splitext(server_path)[1].lower()]
	data, range_l, range_u, end = read_file_bytes(server_path, range_l, range_u)
	return data, mime, range_l, range_u, end
