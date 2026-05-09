from time import perf_counter
import json
import os

from config import config
from log import log
import filesystem as fs

def run(serverPath: str) -> tuple[bytes, str]:
	t = perf_counter()
	def tick(label: str):
		nonlocal t
		now = perf_counter()
		log(f'  {label:<20} {(now - t)*1000: >6.1f} ms')
		t = now

	reqObj = serverPath.replace('..', '')
	isRoot = os.path.abspath(reqObj) == config('root')
	dirUp  = [os.path.abspath(os.path.join(reqObj, '..'))] if not isRoot else []
	tick('abspath/isRoot')

	with os.scandir(reqObj) as itr:
		objs = list(itr)
	tick('scandir')

	dirList    = [os.path.join(reqObj, d.name) for d in objs if d.is_dir()]
	tick('dirList')
	fileList   = [os.path.join(reqObj, f.name) for f in objs if f.is_file() and fs.is_picture(f.name)]
	tick('fileList')
	serverDirs = dirUp + sorted(dirList)
	tick('serverDirs')
	dirUrls    = [fs.to_client_path(d) for d in serverDirs]
	tick('dirUrls')
	imgUrls    = [fs.to_client_path(f) for f in sorted(fileList)]
	tick('imgUrls')

	siblingUrls: list[str] = []
	if not isRoot:
		parentPath = os.path.abspath(os.path.join(reqObj, '..'))
		with os.scandir(parentPath) as parentItr:
			siblingUrls = sorted([fs.to_client_path(e.path) for e in parentItr if e.is_dir()])
	tick('siblings')

	html = fs.read_file_bytes('gallery.html')[0]
	tick('read html')

	data = (html
		.replace(b'{zoomSpeed}',                bytes(config('zoomSpeed'),                                    'utf-8'))
		.replace(b'/*{galleryBackgroundCss}*/', bytes(config('galleryBackgroundCss'),                         'utf-8'))
		.replace(b'/*{viewerBackgroundCss}*/',  bytes(config('viewerBackgroundCss'),                          'utf-8'))
		.replace(b'/*{thumbnailCss}*/',         bytes(config('thumbnailCss'),                                 'utf-8'))
		.replace(b'/*{outlineCss}*/',           bytes(config('outlineCss'),                                   'utf-8'))
		.replace(b'{autoPlayTimer}',            bytes(str(config('autoPlayTimer')),                           'utf-8'))
		.replace(b'{dirUrls}',                  bytes(json.dumps(dirUrls),                                    'utf-8'))
		.replace(b'{imgUrls}',                  bytes(json.dumps(imgUrls),                                    'utf-8'))
		.replace(b'{siblingUrls}',              bytes(json.dumps(siblingUrls),                                'utf-8'))
		.replace(b'{thumbnailPorts}',           bytes(json.dumps([config('port')] + config('thumbnailPorts')),'utf-8'))
		.replace(b'{allowDelete}',              b'true' if config('allowDelete') else b'false'))
	tick('template')

	return data, 'text/html'

