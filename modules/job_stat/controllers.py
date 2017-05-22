from typing import Optional, List

import sqlalchemy
from flask import Blueprint, render_template, current_app
from flask_sqlalchemy import BaseQuery

from modules.job_stat.model import JobStat
from core.job.models import Job
from application.database import global_db
from application.helpers import requires_auth

job_stat_pages = Blueprint('job_stat', __name__
	, template_folder='templates', static_folder='static')

@job_stat_pages.route("/constructor")
@requires_auth
def constructor():
	return render_template("constructor.html")

@job_stat_pages.route("/preset")
@requires_auth
def preset():
	return render_template("preset.html"
		, app_config=current_app.app_config)

def gen_base_query(t_from: int, t_to: int, include: str) -> BaseQuery:
	scoped_duration = sqlalchemy.func.LEAST(Job.t_end, t_to) - sqlalchemy.func.GREATEST(Job.t_start, t_from)

	base_query = global_db.session \
		.query(Job, JobStat, (Job.num_cores * sqlalchemy.func.GREATEST(scoped_duration, 0))
			.label("cores_sec")) \
		.join(JobStat)

	if include == "all":
		return  base_query.filter(Job.t_end > t_from) \
		.filter(Job.t_start < t_to) \
		.subquery()

	elif include == "started":
		return  base_query.filter(Job.t_start > t_from) \
		.filter(Job.t_start < t_to) \
		.subquery()

	elif include == "completed":
		return  base_query.filter(Job.t_end > t_from) \
		.filter(Job.t_end < t_to) \
		.subquery()

	raise KeyError("wrong include value: " + include)

def gen_what(base_query: BaseQuery, metric: str, aggregation_function: str, grouping: List[str]) -> BaseQuery:
	params = []

	function = {
		"min" : sqlalchemy.func.MIN
		, "max" : sqlalchemy.func.MAX
		, "avg" : sqlalchemy.func.AVG
		, "count" : sqlalchemy.func.COUNT
		, "sum" : sqlalchemy.func.SUM
	}[aggregation_function]

	params.append({
		"cores" : function(base_query.c.num_cores).cast(sqlalchemy.Float)
		, "run_time" : function(base_query.c.t_end - base_query.c.t_start).cast(sqlalchemy.Float)
		, "wait_time" : function(base_query.c.t_start - base_query.c.t_submit).cast(sqlalchemy.Float)
		, "cores_sec" : function(base_query.c.cores_sec).cast(sqlalchemy.Float)
		, "jobs" : function(base_query.c.id.distinct()).cast(sqlalchemy.Float)
		, "accounts" : function(base_query.c.account.distinct()).cast(sqlalchemy.Float)
	}[metric].label("{0}_{1}".format(aggregation_function, metric)))

	for group in grouping:
		params.append(group)

	query = global_db.session.query(* params)

	return query

def gen_where(base_query: BaseQuery, query: BaseQuery, partition: Optional[str]
		, account: Optional[str], state: Optional[str]) -> BaseQuery:
	if partition is not None: query = query.filter(base_query.c.partition == partition)
	if account is not None: query = query.filter(base_query.c.account == account)
	if state is not None: query = query.filter(base_query.c.state == state)

	return query

def gen_group(base_query: BaseQuery, query: BaseQuery, grouping: List[str]) -> BaseQuery:
	for group in grouping:
		query = query.group_by(group)

	return query

def generate_query(url_args: dict, metric: str, aggregation_function: str) -> BaseQuery:
	base_query = gen_base_query(url_args["t_from"], url_args["t_to"], url_args.get("include", "all"))

	grouping = url_args.get("grouping")

	if grouping is None or len(grouping) == 0:
		grouping = []
	else:
		grouping = grouping.split(",")

	query = gen_what(base_query, metric, aggregation_function, grouping)

	partition = url_args.get("partition")
	account = url_args.get("account")
	state = url_args.get("state")

	query = gen_where(base_query, query, partition, account, state)
	query = gen_group(base_query, query, grouping)

	return query.order_by(sqlalchemy.desc(aggregation_function + "_" + metric))
