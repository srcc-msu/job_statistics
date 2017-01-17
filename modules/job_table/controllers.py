from functools import partial
from typing import List, Optional
import urllib

from flask import Blueprint, Response, render_template, request, current_app
import flask
from flask_sqlalchemy import BaseQuery
from sqlalchemy import or_
import time

from modules.job_table.helpers import get_color, calculate_job_query_stat
from application.database import global_db
from core.job.models import Job
from core.tag.models import JobTag
from core.monitoring.models import JobPerformance
from core.tag.constants import TAG_SEPARATOR

job_table_pages = Blueprint('job_table', __name__
	, template_folder='templates', static_folder='static')

def construct_general_query(accounts: str, date_from: Optional[int], date_to: Optional[int]) -> BaseQuery:
	query = global_db.session.query(Job, JobTag, JobPerformance).join(JobTag).join(JobPerformance)

	query = query.filter(Job.t_start > date_from)
	query = query.filter(Job.t_end < date_to)

	if len(accounts) > 0:
		accounts = accounts.split(",")
		query = query.filter(Job.account.in_(accounts))

	return query

def construct_filtered_query(query: BaseQuery, req_tags: List[str], opt_tags: List[str], no_tags: List[str]) -> BaseQuery:
	for tag in req_tags:
		query = query.filter(JobTag.tags.contains(tag))

	# --

	opt_tags_checks = []

	for tag in opt_tags:
		opt_tags_checks.append(JobTag.tags.contains(tag))

	query = query.filter(or_(*opt_tags_checks))

	# --

	for tag in no_tags:
		query = query.filter(~JobTag.tags.contains(tag))

	return query

@job_table_pages.route("/table/")
def table_redirect():
	query = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""

	return flask.redirect(flask.url_for("job_table.table", page=0) + query)

@job_table_pages.route("/table/page/<int:page>")
def table(page) -> Response:
	PAGE_SIZE = 50

	data = request.args.to_dict()

	reload = False

	if "date_to" not in data or data["date_to"] == 0:
		data["date_to"] = int((int(time.time()) + 86400) / 86400) * 86400
		reload = True

	if "date_from" not in data or data["date_from"] == 0:
		data["date_from"] = int((data["date_to"] - 86400 * 3) / 86400) * 86400
		reload = True

	if reload:
		return flask.redirect(request.path + "?" + urllib.parse.urlencode(data))

	accounts = data.get("accounts", "")

	def extract_tag(data: dict, name: str):
		tags = data.get(name)

		if tags is None or len(tags) == 0:
			return []
		return tags.split(TAG_SEPARATOR)

	req_tags = extract_tag(data, "req_tags")
	opt_tags = extract_tag(data, "opt_tags")
	no_tags = extract_tag(data, "no_tags")

#   query construction

	query = construct_general_query(accounts, data["date_from"], data["date_to"])
	query = construct_filtered_query(query, req_tags, opt_tags, no_tags)

	query = query.filter(Job.state != "RUNNING")

	query_stat = calculate_job_query_stat(request.query_string, query)

	show_query = query.order_by(Job.t_end.desc()).offset(page * PAGE_SIZE).limit(PAGE_SIZE)

	query = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""

	return render_template("job_table.html"
		, jobs=show_query.all()
		, query_stat=query_stat
		, prev_page = flask.url_for("job_table.table", page = page-1) + query if page > 0 else None
		, next_page = flask.url_for("job_table.table", page = page+1) + query
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
