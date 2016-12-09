from functools import partial
from typing import List, Optional

from flask import Blueprint, Response, render_template, request, current_app
import flask
from flask_sqlalchemy import BaseQuery
from sqlalchemy import or_

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

	if date_from is not None:
		query = query.filter(Job.t_start > date_from)

	if date_to is not None:
		query = query.filter(Job.t_end < date_to)

	if accounts is not None:
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

@job_table_pages.route("/table")
def table_redirect():
	return flask.redirect(flask.url_for(table, page=0))

@job_table_pages.route("/table/<int:page>")
def table(page) -> Response:
	PAGE_SIZE = 50

	date_from = request.args.get("date_from")
	date_to = request.args.get("date_to")
	accounts = request.args.get("accounts")

	def extract_tag(name: str):
		tags = request.args.get(name)

		if tags is None or len(tags) == 0:
			return []
		return tags.split(TAG_SEPARATOR)

	req_tags = extract_tag("req_tags")
	opt_tags = extract_tag("opt_tags")
	no_tags = extract_tag("no_tags")

#   query construction

	query = construct_general_query(accounts, date_from, date_to)
	query = construct_filtered_query(query, req_tags, opt_tags, no_tags)

	min_len = current_app.app_config.general["aggregation_interval"] * 3

	query = query.filter(Job.state != "RUNNING").filter(Job.t_end - Job.t_start > min_len)

	query_stat = calculate_job_query_stat(query)

	show_query = query.order_by(Job.t_end.desc()).offset(page * PAGE_SIZE).limit(PAGE_SIZE)

	return render_template("job_table.html"
		, jobs=show_query.all()
		, query_stat=query_stat
		, prev_page = flask.url_for("job_table.table", page = page-1) if page > 0 else None
		, next_page = flask.url_for("job_table.table", page = page+1)
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
