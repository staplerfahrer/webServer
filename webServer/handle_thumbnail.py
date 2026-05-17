import io
import os
# pip install types-Pillow to fix Pylance
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from random import randrange
import subprocess
import traceback

from config import config
from log import log


SHARPEN = 1.3


def run(serverPath: str) -> tuple[bytes, str]:
	log(f'handle_thumbnail {serverPath}')
	tnWidthHeight = config('thumbnailWidthHeight')
	tnColor = config('thumbBackgroundColor')
	reqObj  = serverPath[:-3]
	file_name = os.path.split(reqObj)[-1:][0]
	file_extension = os.path.splitext(reqObj)[1][1:].upper()

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
		text = f'{file_extension}  {img.size[0]} x {img.size[1]}'

		# convert to RGB
		if img.mode in ['P', 'CMYK']:
			img = img.convert('RGB')
		if img.mode in ['PA', 'LA']:
			img = img.convert('RGBA')
		has_alpha = img.mode in ('RGBA', 'LA', 'PA') or \
			(img.mode == 'P' and 'transparency' in img.info)

		# generate thumbnail
		# https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.thumbnail
		img.thumbnail(size=tnWidthHeight, resample=Image.Resampling.LANCZOS, reducing_gap=1.0)

		canvas = Image.new(img.mode, tnWidthHeight, tnColor if img.mode == 'RGB' else 0)
		left   = (tnWidthHeight[0] - img.size[0]) // 2
		top    = (tnWidthHeight[1] - img.size[1]) // 2
		canvas.paste(img, (left, top))
		draw   = ImageDraw.Draw(canvas)
		font   = ImageFont.load_default()
		text_box = draw.textbbox((0, 0), text, font=font)
		tw, th = text_box[2] - text_box[0], text_box[3] - text_box[1]
		font_color = (95, 95, 95) if canvas.mode in ('RGB', 'RGBA') else 95
		draw.text((tnWidthHeight[0] - tw - 2, tnWidthHeight[1] - th - 5), text, font=font, fill=font_color) # pyright: ignore[reportUnknownMemberType]

		# sharpen
		canvas = ImageEnhance.Sharpness(canvas).enhance(factor=SHARPEN)
	except Exception:
		log(f'Exception at "make a thumbnail": {traceback.format_exc()}')
		reqObj = 'resources\\thumbnail-bad-picture.png'
		has_alpha = True
		img  = Image.open(reqObj)
		text = f'BAD FILE  {file_name}'
		canvas = Image.new(img.mode, tnWidthHeight, tnColor if img.mode == 'RGB' else 0)
		left   = (tnWidthHeight[0] - img.size[0]) // 2
		top    = (tnWidthHeight[1] - img.size[1]) // 2
		canvas.paste(img, (left, top))
		draw   = ImageDraw.Draw(canvas)
		font   = ImageFont.load_default()
		text_box = draw.textbbox((0, 0), text, font=font)
		tw, th = text_box[2] - text_box[0], text_box[3] - text_box[1]
		font_color = (95, 95, 95) if canvas.mode in ('RGB', 'RGBA') else 95
		draw.text((tnWidthHeight[0] - tw - 2, tnWidthHeight[1] - th - 5), text, font=font, fill=font_color) # pyright: ignore[reportUnknownMemberType]

	if reqObj.startswith('ffThumb') and os.path.exists(reqObj):
		os.unlink(reqObj)

	buf = io.BytesIO()
	if has_alpha:
		canvas.save(buf, format='png', optimize=False, compress_level=9)
		log('returning png')
		return buf.getvalue(), 'image/png'
	else:
		canvas.save(buf, format='jpeg', quality=90, optimize=False, progressive=True, subsampling=1)
		log('returning jpeg')
		return buf.getvalue(), 'image/jpeg'

