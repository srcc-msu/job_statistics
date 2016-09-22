from functools import partial
from typing import List, Optional

from flask import Blueprint, Response, render_template, request, current_app
from flask_sqlalchemy import BaseQuery
from sqlalchemy import or_

from core.tag.constants import TAG_SEPARATOR
from modules.job_table.helpers import get_color
from database import global_db
from core.job.models import Job
from core.tag.models import JobTag
from core.monitoring.models import JobPerformance

job_table_pages = Blueprint('job_table', __name__
	, template_folder='templates', static_folder='static')

def construct_filtered_query(t_from: Optional[int], t_to: Optional[int]
		, req_tags: List[str], opt_tags: List[str], no_tags: List[str]) -> BaseQuery:
	query = global_db.session.query(Job, JobTag, JobPerformance).join(JobTag).join(JobPerformance)

	if t_from is not None:
		query = query.filter(Job.t_start > t_from)

	if t_to is not None:
		query = query.filter(Job.t_end < t_to)

	# --

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
def jobs() -> Response:
	t_from = request.args.get("t_from")
	t_to = request.args.get("t_to")

	def extract_tag(name: str):
		tags = request.args.get(name)

		if tags is None or len(tags) == 0:
			return []
		return tags.split(TAG_SEPARATOR)

	req_tags = extract_tag("req_tags")
	opt_tags = extract_tag("opt_tags")
	no_tags = extract_tag("no_tags")

	sensors = ["avg_cpu_user", "avg_cpu_flops", "avg_cpu_perf_l1d_repl", "avg_llc_miss", "avg_mem_load",
		"avg_mem_store", "avg_ib_rcv_data", "avg_ib_xmit_data", "avg_loadavg", "avg_gpu_load"]

	return render_template("job_table.html"
		, jobs=construct_filtered_query(t_from, t_to, req_tags, opt_tags, no_tags).all()
		, sensors=sensors
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
