import csv
import datetime
import io
import threading
from typing import List

from datetime import timedelta
from flask import make_response, request, current_app, Response
from functools import update_wrapper, wraps

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

import time

def __bg_wrapper(function, params):
	__bg_wrapper.bg_count += 1
	print("{} started in {}, running: {}, params: {}".format(function.__name__, time.strftime("%Y-%m-%d %H:%M %s"), __bg_wrapper.bg_count, params))

	start = time.time()
	try:
		function(*params)
	except:
		pass
	end = time.time()

	__bg_wrapper.bg_count -= 1
	print("{} finished in {:.2f} seconds, running: {}".format(function.__name__, end - start, __bg_wrapper.bg_count, params))

__bg_wrapper.bg_count = 0

def background(function, params):

	thread = threading.Thread(target=__bg_wrapper, args=(function, params,))
	thread.daemon = True
	thread.start()

def check_auth(username, password):
	"""This function is called to check if a username /
	password combination is valid.
	"""
	return username == current_app.config.get("LOGIN") and password == current_app.config.get("PASSWORD")

def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		auth = request.authorization
		if not auth:
			return authenticate()
		if not check_auth(auth.username, auth.password):
			print("bad auth attempt: {0} {1}".format(auth.username, auth.password))
			return authenticate()
		return f(*args, **kwargs)
	return decorated
