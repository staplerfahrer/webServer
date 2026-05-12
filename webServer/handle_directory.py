from time import perf_counter
import json
import os

from config import config
from log import log
import filesystem as fs

def run(server_path: str) -> tuple[bytes, str]:
	t = perf_counter()
	def tick(label: str):
		nonlocal t
		now = perf_counter()
		log(f'  {label:<20} {(now - t)*1000: >6.1f} ms')
		t = now

	# discover directories & files
	req_obj = server_path.replace('..', '')
	is_root = os.path.abspath(req_obj) == config('root')
	parent_path = [os.path.abspath(os.path.join(req_obj, '..'))] if not is_root else []
	tick('abspath/isRoot')

	with os.scandir(req_obj) as itr:
		objs = list(itr)
	tick('scandir')

	dir_list    = [os.path.join(req_obj, d.name) for d in objs if d.is_dir()]
	tick('dirList')
	file_list   = [os.path.join(req_obj, f.name) for f in objs if f.is_file() and fs.is_picture(f.name)]
	tick('fileList')
	server_dirs = parent_path + sorted(dir_list)
	tick('serverDirs')
	dir_urls    = [fs.to_client_path(d) for d in server_dirs]
	tick('dirUrls')
	img_urls    = [fs.to_client_path(f) for f in sorted(file_list)]
	tick('imgUrls')

	sibling_urls: list[str] = []
	if not is_root:
		with os.scandir(parent_path[0]) as parent_itr:
			sibling_urls = sorted([fs.to_client_path(e.path) for e in parent_itr if e.is_dir()])
	tick('siblings')

	# produce HTML
	gallery_html = fs.read_file_bytes('gallery.html')[0]
	tick('read gallery_html')

	thumbnail_html = fs.read_file_bytes('thumbnail.html')[0]
	tick('read thumbnail_html')
	data = (gallery_html
		.replace(b'{thumbnailHtml}', thumbnail_html)
		.replace(b'/*{thumbnailCss}*/', bytes(config('thumbnailCss'), 'utf-8'))
		.replace(b'{thumbnailPorts}', bytes(json.dumps(config('thumbnailPorts')), 'utf-8'))
		.replace(b'/*{thumbnailWidth}*/', bytes(str(config('thumbWidthHeight')[0]), 'utf-8'))
		)

	data = (data
		.replace(b'{allowDelete}', b'true' if config('allowDelete') else b'false')
		.replace(b'{autoPlayTimer}', bytes(str(config('autoPlayTimer')), 'utf-8'))
		.replace(b'{dirUrls}', bytes(json.dumps(dir_urls), 'utf-8'))
		.replace(b'{imgUrls}', bytes(json.dumps(img_urls), 'utf-8'))
		.replace(b'{siblingUrls}', bytes(json.dumps(sibling_urls), 'utf-8'))
		.replace(b'{zoomSpeed}', bytes(config('zoomSpeed'), 'utf-8'))
		.replace(b'/*{galleryBackgroundCss}*/', bytes(config('galleryBackgroundCss'), 'utf-8'))
		.replace(b'/*{selectionOutlineCss}*/', bytes(config('selectionOutlineCss'), 'utf-8'))
		.replace(b'/*{viewerBackgroundCss}*/', bytes(config('viewerBackgroundCss'), 'utf-8'))
		)
	tick('template')

	return data, 'text/html'

