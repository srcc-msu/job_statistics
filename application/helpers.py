import csv
import datetime
import io
import multiprocessing
import queue
import threading
import traceback
from typing import List
import time

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
import sys

def gen_csv_response(header: List[dict], data: List[List]):
	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(map(lambda x: x["name"], header))

	for row in data:
		writer.writerow(row)

	result = make_response(output.getvalue())
	result.headers["Content-type"] = "text" # TODO: text is easier for debugging - browsers will not try to save it
	return result

def app_log(string: str):
	print(time.strftime('[%x %X]'), "app: " + string)

def ts2datetime(ts: int) -> str:
	return datetime.datetime.fromtimestamp(float(ts)).strftime('%Y-%m-%d %H:%M:%S')

def float2(float) -> str:
	if float is None:
		return "None"
	return  "{0:.2f}".format(float)

def crossdomain(origin=None, methods=None, headers=None,
				max_age=21600, attach_to_all=True,
				automatic_options=True):
#   http://flask.pocoo.org/snippets/56/
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, str):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, str):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers

			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator

def __background(timeout):
	while True:
		try:
			function, params = __background.queue.get(block=True)
			p = multiprocessing.Process(target=function, args=params)
			p.start()
			p.join(timeout)

			if p.is_alive():
				print("killing long background process, params: ", params)

				p.terminate()
				p.join()

		except Exception:
			traceback.print_exc(file=sys.stderr)

__background.queue = None

def background(function, params):
	if __background.queue is None:
		__background.queue = queue.Queue()

		thread = threading.Thread(target=__background, args=(300,))
		thread.daemon = True
		thread.start()

	__background.queue.put((function, params), block=False)
