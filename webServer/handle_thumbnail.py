import io
import os
# pip install types-Pillow to fix Pylance
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from random import randrange
import subprocess
import traceback

from config import config
from log import log


def run(serverPath: str) -> tuple[bytes, str]:
	log(f'handle_thumbnail {serverPath}')
	tnSize  = config('thumbSize')
	tnColor = config('thumbBackgroundColor')
	reqObj  = serverPath[:-3]

	# if video, extract a frame
	try:
		if not (reqObj.endswith('.mp4') or reqObj.endswith('.m4v') or reqObj.endswith('.mov') or reqObj.endswith('.ts')):
			raise Exception('not a video')
		ffOutput  = f'ffThumb{randrange(1000000, 9999999)}.jpg'
		timeStamp = '00:00:10.000'
		for _ in range(2):
			subprocess.call(['resources/ffmpeg.exe', '-i', reqObj, '-ss', timeStamp, '-update', '1', '-vframes', '1', ffOutput])
			if os.path.exists(ffOutput):
				break
			timeStamp = '00:00:01.000'
		reqObj = ffOutput
	except Exception as e:
		if 'not a video' not in e.args:
			log(f'Exception at "video thumbnail": {traceback.format_exc()}')

	# make a thumbnail
	try:
		img  = Image.open(reqObj)
		text = f'{img.size[0]} x {img.size[1]}'

		# convert to RGB
		if img.mode == 'P':
			img = img.convert('RGB')

		# generate thumbnail
		# https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.thumbnail
		img.thumbnail(size=tnSize, resample=Image.Resampling.LANCZOS, reducing_gap=1.0)

		canvas = Image.new(img.mode, tnSize, tnColor if img.mode == 'RGB' else 0)
		left   = (tnSize[0] - img.size[0]) // 2
		top    = (tnSize[1] - img.size[1]) // 2
		canvas.paste(img, (left, top))
		draw   = ImageDraw.Draw(canvas)
		font   = ImageFont.load_default()
		text_box = draw.textbbox((0, 0), text, font=font)
		tw, th = text_box[2] - text_box[0], text_box[3] - text_box[1]
		font_color = (95, 95, 95) if canvas.mode in ('RGB', 'RGBA') else 95
		draw.text((tnSize[0] - tw - 2, tnSize[1] - th - 5), text, font=font, fill=font_color) # pyright: ignore[reportUnknownMemberType]

		# sharpen
		canvas = ImageEnhance.Sharpness(canvas).enhance(factor=1.7)
	except Exception:
		log(f'Exception at "make a thumbnail": {traceback.format_exc()}')
		canvas = Image.new('RGB', tnSize)

	if reqObj.startswith('ffThumb') and os.path.exists(reqObj):
		os.unlink(reqObj)

	buf = io.BytesIO()
	if canvas.mode == 'RGB':
		canvas.save(buf, format='jpeg', quality=90, optimize=False, progressive=True, subsampling=1)
		return buf.getvalue(), 'image/jpeg'
	else:
		canvas.save(buf, format='png', optimize=False, compress_level=9)
		return buf.getvalue(), 'image/png'

