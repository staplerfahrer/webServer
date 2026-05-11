from collections import deque
from shutil import get_terminal_size
from socket import create_server, socket
from time import sleep, perf_counter
import msvcrt
import os
import subprocess
import sys
import threading
import traceback


from config import config
import handle_request
import stats
from log import log


THREAD_COUNT = 100
# TODO: MRU in cookie
# TODO: fix video player full-screen
# TODO: fix video player keyboard seek


# The thumbnails for every image are already loaded in the browser cache — addImg loaded them to build the gallery. In
#   updateViewed, instead of immediately hiding vi while the full-res fetches, we could set vi.src to the thumbnail URL
#   first (instant, from cache), then load the full-res in a background Image object and swap it in when ready.

#   The one complication: vi.onload = zoomStyle uses vi.naturalWidth/Height for the zoom animation, so we'd need to
#   suppress it for the thumbnail swap and only let it fire for the full-res. A simple boolean flag handles that.

#   A secondary win while we're there: cacheNext only pre-caches forward (+1 to +10) with a 2-second delay — ArrowLeft is
#   never pre-cached, and the delay means ArrowRight only benefits if you paused. Reducing that delay to ~100ms and adding
#    one step backward would help a lot too.

queue         : deque[tuple[socket, str]] = deque()
thumbnailQueue: deque[tuple[socket, str]] = deque()
busyCount     : int                       = 0
busyLock      : threading.Lock            = threading.Lock()


def main():
	try:
		os.system('cls')
		if config('autoStart'):
			subprocess.call(['explorer', 'http://127.0.0.1'])

		# UI thread
		threading.Thread(
			target=ui,
			name='UI',
			daemon=True).start()

		# thumbnail threads
		for port in config('thumbnailPorts'):
			threading.Thread(
				target=listen,
				args=(config('address'), port),
				name=f'Listener {config("address")}:{port}',
				daemon=True).start()

		workerThreads = [threading.Thread(
			target=thread_worker,
			name=f'Worker Bee {i}')
			for i in range(THREAD_COUNT)]
		[t.start() for t in workerThreads]
		listen(config('address'), config('port'))
		[t.join() for t in workerThreads]
	except KeyboardInterrupt:
		log('KeyboardInterrupt')
		os._exit(0)
	except Exception:
		log(f'main() exception {traceback.format_exc()}')


def listen(address: str, port: int):
	# https://docs.python.org/3/library/socket.html
	with create_server((address, port)) as serv:
		# timeout because browsers may start blocking, empty request connections
		serv.settimeout(1)
		log(f'Listen...{serv} timeout {serv.timeout}')
		while True:
			try:
				conn, addr = serv.accept()
				log(f'Connected...{addr}')
				# https://stackoverflow.com/questions/20289981/python-sockets-stop-recv-from-hanging
				req = str(conn.recv(1_048_576), 'utf-8')
				if req == '':
					log('blank request')
					continue
				if '?tn HTTP/1.1' in req:
					thumbnailQueue.append((conn, req))
				else:
					queue.append((conn, req))
			except TimeoutError:
				# timeout is essential, see above
				pass
			except KeyboardInterrupt:
				log('KeyboardInterrupt')
				os._exit(0)
			except Exception:
				log(traceback.format_exc())


def thread_worker():
	global busyCount
	while True:
		try:
			sleep(0.01)
			if not len(queue) and not len(thumbnailQueue):
				continue

			with busyLock:
				busyCount += 1

			startTime = perf_counter()

			try:
				conn, req = queue.popleft()
			except IndexError:
				conn, req = thumbnailQueue.popleft()
			firstLine = req.split('\r\n', 1)[0]
			if firstLine.startswith('GET ') and firstLine.endswith(' HTTP/1.1'):
				log('Popping get ' + firstLine[4:-9])
			else:
				log('Popping job ' + req.replace('\r\n', '\\n'))
			bytes_ = handle_request.build_response_bytes(req)
			conn.sendall(bytes_) # , flags=
			conn.close()

			elapsed = perf_counter() - startTime
			with stats.lock:
				stats.bytesServed      += len(bytes_)
				stats.processingTime   += elapsed
				stats.requestsServed   += 1
				if '?tn HTTP/1.1' in req:
					stats.thumbnailsServed += 1

			log(f'Finished in {elapsed:.3f} s')

			with busyLock:
				busyCount -= 1
		except:
			log(f'threadWorker() exception {traceback.format_exc()}')


# MARK: server UI
def ui():
	# hotkey daemon
	threading.Thread(
		target=hotkeyListener,
		name='Hotkey Listener',
		daemon=True).start()

	cols = get_terminal_size().columns
	sec_per_frame = 1 / 60
	last_rq = 0
	req_sec_avg = 0
	while True:
		sleep(sec_per_frame)
		cols = get_terminal_size().columns
		title = f' hoard Media Gallery serving at http://{config("address")}:{config("port")} '
		pad = (cols - len(title)) // 2
		title = f'{"=" * pad}{title}{"=" * pad}'
		requestQueue = len(queue) + len(thumbnailQueue)
		with busyLock:
			busyWorkers = busyCount
		with stats.lock:
			tn  = stats.thumbnailsServed
			b   = stats.bytesServed
			pt  = stats.processingTime
			rq  = stats.requestsServed
		req_sec = (rq - last_rq) / sec_per_frame
		req_sec_avg = req_sec * 0.005 + req_sec_avg * 0.995
		last_rq = rq
		statsLine = f'{tn:,} tn  {b:,} B  {pt:.1f} s  {req_sec_avg:.0f} req/s'
		sys.stdout.write(
			f'\033[5A'
			f'{title}\n'
			f'Press <CTRL+C> to quit, <CTRL+R> to restart.\n'
			f'\r\033[K{requestQueue:>4} queue   {"Q" * min(requestQueue, cols - 20)}\n'
			f'\r\033[K{busyWorkers :>4} workers {"W" * min(busyWorkers, cols - 20)}\n'
			f'\r\033[K{statsLine}\n'
		)
		sys.stdout.flush()


def hotkeyListener():
	while True:
		sleep(0.05)
		if not msvcrt.kbhit():
			continue
		ch = msvcrt.getwch()
		if ch == '\x12':  # Ctrl+R
			log('Restarting...')
			os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == '__main__':
	main()
