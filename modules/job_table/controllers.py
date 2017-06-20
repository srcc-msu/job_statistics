from functools import partial
import urllib
import time

from flask import Blueprint, Response, render_template, request, current_app
import flask

from modules.job_table.model import construct_full_table_query, calculate_job_query_stat
from modules.job_table.helpers import extract_string_list, extract_number
from core.job.helpers import hash2id, id2hash, id2username
from modules.job_table.helpers import get_color
from application.database import global_db
from core.job.models import Job
from core.tag.models import JobTag
from core.monitoring.models import JobPerformance
from application.helpers import requires_auth

job_table_pages = Blueprint('job_table', __name__
	, template_folder='templates', static_folder='static')


@job_table_pages.route("/table")
@requires_auth
def table_redirect():
	query = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""

	return flask.redirect(flask.url_for("job_table.get_table", _external=True, page=0) + query)

@job_table_pages.route("/share/<string:hash>")
def anon_table_redirect(hash):
	query = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""

	return flask.redirect(flask.url_for("job_table.get_anon_table", _external=True, hash=hash, page=0) + query)

def clean_user_request(data: dict) -> dict:
	filter = {}

	filter["date_from"] = extract_number(data, "date_from", None)
	filter["date_to"] = extract_number(data, "date_to", None)

	filter["req_tags"] = extract_string_list(data, "req_tags")
	filter["opt_tags"] = extract_string_list(data, "opt_tags")
	filter["no_tags"] = extract_string_list(data, "no_tags")

	filter["accounts"] = extract_string_list(data, "accounts")
	filter["partitions"] = extract_string_list(data, "partitions")
	filter["states"] = extract_string_list(data, "states")

	return filter

def convert_js_timestamp(filter: dict) -> dict:
	try:
		filter["date_to"] //= 1000 # remove milliseconds
	except TypeError:
		pass # ignore None

	try:
		filter["date_from"] //= 1000
	except TypeError:
		pass

	return filter

def encode_filter(filter):
	result = {}

	result["date_from"] = filter["date_from"]
	result["date_to"] = filter["date_to"]

	result["req_tags"] = ",".join(filter["req_tags"])
	result["opt_tags"] = ",".join(filter["opt_tags"])
	result["no_tags"] = ",".join(filter["no_tags"])

	result["accounts"] = ",".join(filter["accounts"])
	result["partitions"] = ",".join(filter["partitions"])
	result["states"] = ",".join(filter["states"])

	return result

def job_table_common_post():
	data = request.form.to_dict()
	filter = clean_user_request(data)
	filter = convert_js_timestamp(filter)

	url_params = encode_filter(filter)
	return flask.redirect(request.path + "?" + urllib.parse.urlencode(url_params))

def get_job_table_filter():
	data = request.args.to_dict()
	filter = clean_user_request(data)

	if filter["date_from"] is None:
		filter["date_from"] = int(time.time()) - 86400 * 7

	return filter

def get_job_table_query(filter):
	query = global_db.session.query(Job, JobTag, JobPerformance).join(JobTag).join(JobPerformance)

	query = construct_full_table_query(query, filter)

	query = query.filter(Job.state != "RUNNING")

	return query


@job_table_pages.route("/table/page/<int:page>", methods=["POST"])
@requires_auth
def post_table(page: int) -> Response:
	return job_table_common_post()

@job_table_pages.route("/table/page/<int:page>", methods=["GET"])
@requires_auth
def get_table(page: int) -> Response:
	PAGE_SIZE = 50

	query_url = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""
	prev_page_link = flask.url_for("job_table.get_table", _external=True, page = page-1) + query_url if page > 0 else None
	next_page_link = flask.url_for("job_table.get_table", _external=True, page = page+1) + query_url

	filter = get_job_table_filter()
	query = get_job_table_query(filter)

	query_stat = calculate_job_query_stat(request.query_string, query)

	show_query = query.order_by(Job.t_end.desc()).offset(page * PAGE_SIZE).limit(PAGE_SIZE)

	return render_template("job_table_full.html"
		, jobs=show_query.all()
		, query_stat=query_stat
		, prev_page_link = prev_page_link
		, next_page_link = next_page_link
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))

@job_table_pages.route("/share/<string:hash>/<int:page>", methods=["POST"])
def post_anon_table(hash: str, page: int) -> Response:
	return job_table_common_post()

@job_table_pages.route("/share/<string:hash>/<int:page>", methods=["GET"])
def get_anon_table(hash: str, page: int) -> Response:
	PAGE_SIZE = 50

	query_url = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""
	prev_page_link = flask.url_for("job_table.get_anon_table", _external=True, hash = hash, page = page-1) + query_url if page > 0 else None
	next_page_link = flask.url_for("job_table.get_anon_table", _external=True, hash = hash, page = page+1) + query_url

	filter = get_job_table_filter()
	filter["accounts"] = [id2username(hash2id(hash))]

	query = get_job_table_query(filter)

	query_stat = calculate_job_query_stat(request.query_string, query)

	show_query = query.order_by(Job.t_end.desc()).offset(page * PAGE_SIZE).limit(PAGE_SIZE)

	return render_template("job_table_anon.html"
		, jobs=show_query.all()
		, query_stat=query_stat
		, prev_page_link = prev_page_link
		, next_page_link = next_page_link
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"])
		, id2hash=id2hash)

@job_table_pages.route("/timeline", methods=["POST"])
@requires_auth
def post_timeline() -> Response:
	return job_table_common_post()

@job_table_pages.route("/timeline", methods=["GET"])
@requires_auth
def timeline() -> Response:
	filter = get_job_table_filter()
	query = get_job_table_query(filter)
	query_stat = calculate_job_query_stat(request.query_string, query)

	show_query = query.order_by(Job.t_end.desc())

	return render_template("timeline.html"
		, jobs=show_query.all()
		, query_stat=query_stat
		, app_config=current_app.app_config)

@job_table_pages.route("/queue_timeline", methods=["POST"])
@requires_auth
def post_queue_timeline() -> Response:
	return job_table_common_post()

@job_table_pages.route("/queue_timeline", methods=["GET"])
@requires_auth
def queue_timeline() -> Response:
	filter = get_job_table_filter()
	query = get_job_table_query(filter)
	query_stat = calculate_job_query_stat(request.query_string, query)

	show_query = query.order_by(Job.t_end.desc())

	return render_template("queue_timeline.html"
		, jobs=show_query.all()
		, query_stat=query_stat
		, app_config=current_app.app_config)
