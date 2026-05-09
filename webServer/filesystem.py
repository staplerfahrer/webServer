import os
import traceback

from config import config
from log import log

_MIME: dict[str, str] = {
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


def to_client_path(fn: str) -> str:
	url = fn.replace(config('root'), '').replace('\\', '/')
	return url if url else '/'


def to_server_path(url: str) -> str:
	return config('root') + url.replace('/', '\\')


def read_file_bytes(fileName: str, rangeL: int | None = None, rangeU: int | None = None) -> tuple[bytes, int | None, int | None, int | None]:
	try:
		with open(fileName, 'rb') as f:
			if rangeL is not None:
				f.seek(0, os.SEEK_END)
				end = f.tell()
				if rangeL > end:
					return bytes(), end - 1, end - 1, end - 1
				if rangeU is None or rangeU >= end:
					#rangeU may be None (https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Range)
					rangeU = end - 1
				f.seek(rangeL)
				return f.read(rangeU - rangeL + 1), rangeL, rangeU, end
			return f.read(), None, None, None
	except Exception:
		log(f'Exception at "__readFileBytes": {traceback.format_exc()}')
		return b'', None, None, None


def delete_file(serverPath: str) -> tuple[bytes, str]:
	if not config('allowDelete'):
		return b'disabled', 'text/plain'
	try:
		target = serverPath[:-4]
		os.rename(target, target + '.deleted')
		return b'ok', 'text/plain'
	except Exception:
		log(f'Exception at delete: {traceback.format_exc()}')
		return b'error', 'text/plain'


def is_picture(fileName: str) -> bool:
	parts = os.path.splitext(fileName)
	return parts[1].lower() in _MIME


def serve_file(serverPath: str, rangeL: int | None, rangeU: int | None) -> tuple[bytes, str, int | None, int | None, int | None]:
	mime = _MIME[os.path.splitext(serverPath)[1].lower()]
	data, rangeL, rangeU, end = read_file_bytes(serverPath, rangeL, rangeU)
	return data, mime, rangeL, rangeU, end
