import csv
import io
from typing import List
import time

from flask import make_response

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
