from functools import partial
import urllib
import time

from flask import Blueprint, Response, render_template, request, current_app
import flask

from api.job_table.controllers import construct_full_table_query
from modules.job_table.helpers import get_color, calculate_job_query_stat
from application.database import global_db
from core.job.models import Job
from core.tag.models import JobTag
from core.monitoring.models import JobPerformance

job_table_pages = Blueprint('job_table', __name__
	, template_folder='templates', static_folder='static')


@job_table_pages.route("/table/")
def table_redirect():
	query = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""

	return flask.redirect(flask.url_for("job_table.table", page=0) + query)

@job_table_pages.route("/table/page/<int:page>", methods=["GET", "POST"])
def table(page: int) -> Response:
	PAGE_SIZE = 50

	if request.method == "POST":
		data = request.form.to_dict()

		try:
			data["date_from"] = int(int(data["date_from"]) / 1000)
		except (KeyError, ValueError):
			pass

		try:
			data["date_to"] = int(int(data["date_to"]) / 1000)
		except (KeyError, ValueError):
			pass

		return flask.redirect(request.path + "?" + urllib.parse.urlencode(data))

	elif request.method == "GET":
		data = request.args.to_dict()

		if "date_from" not in data:
			data["date_from"] = int(time.time()) - 86400 * 7;
			return flask.redirect(request.path + "?" + urllib.parse.urlencode(data))

		query = global_db.session.query(Job, JobTag, JobPerformance).join(JobTag).join(JobPerformance)

		query = construct_full_table_query(query, data)

		query = query.filter(Job.state != "RUNNING")

		query_stat = calculate_job_query_stat(request.query_string, query)

		show_query = query.order_by(Job.t_end.desc()).offset(page * PAGE_SIZE).limit(PAGE_SIZE)

		query_url = "?" + request.query_string.decode("utf-8") if len(request.query_string) > 0 else ""

		return render_template("job_table.html"
			, jobs=show_query.all()
			, query_stat=query_stat
			, prev_page = flask.url_for("job_table.table", page = page-1) + query_url if page > 0 else None
			, next_page = flask.url_for("job_table.table", page = page+1) + query_url
			, app_config=current_app.app_config
			, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
