from log import log
from typing import Any
from random import randrange
import glob
import json
import os
import traceback


cached = False
config_cache: dict[str, Any] = {}

_VIDEO_TN_PREFIX = 'ffThumb'
_VIDEO_TN_EXT    = '.jpg'


def video_thumbnail_path() -> str:
	return f'{_VIDEO_TN_PREFIX}{randrange(1000000, 9999999)}{_VIDEO_TN_EXT}'


def _cleanup_leftover_thumbnails() -> None:
	for path in glob.glob(f'{_VIDEO_TN_PREFIX}*{_VIDEO_TN_EXT}'):
		try:
			os.remove(path)
			log(f'Removed leftover video thumbnail: {path}')
		except Exception:
			log(f'Failed to remove {path}: {traceback.format_exc()}')

_cleanup_leftover_thumbnails()


def config(name: str) -> Any:
	global cached, config_cache

	try:

		if not cached:
			with open('config.json', 'r') as f:
				config_cache = json.load(f)
			cached = True

		return config_cache[name]

	except:
		log(traceback.format_exc())
		raise
