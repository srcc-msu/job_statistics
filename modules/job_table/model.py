from typing import List, Optional

from flask import jsonify, request
from flask import Blueprint, Response
from flask_sqlalchemy import BaseQuery
from sqlalchemy import or_

from core.job.models import Job
from core.tag.models import JobTag
from application.helpers import crossdomain

job_table_api_pages = Blueprint('job_table_api', __name__
	, template_folder='templates')

def query_apply_common_filter(query: BaseQuery, accounts: List[str], partitions: List[str], states: List[str]) -> BaseQuery:
	if len(accounts) > 0:
		query = query.filter(Job.account.in_(accounts))

	if len(partitions) > 0:
		query = query.filter(Job.partition.in_(partitions))

	if len(states) > 0:
		query = query.filter(Job.state.in_(states))

	return query

def query_apply_date_filter(query: BaseQuery, date_from: Optional[int], date_to: Optional[int]) -> BaseQuery:
	if date_from is not None:
		query = query.filter(Job.t_end > date_from)

	if date_to is not None:
		query = query.filter(Job.t_end < date_to)

	return query

def query_apply_tags_filter(query: BaseQuery, req_tags: List[str], opt_tags: List[str], no_tags: List[str]) -> BaseQuery:
	for tag in req_tags:
		query = query.filter(JobTag.tags.contains(tag))

	# --

	opt_tags_checks = []

	for tag in opt_tags:
		opt_tags_checks.append(JobTag.tags.contains(tag))

	if len(opt_tags_checks) > 0:
		query = query.filter(or_(*opt_tags_checks))

	# --

	for tag in no_tags:
		query = query.filter(~JobTag.tags.contains(tag))

	return query

def construct_job_table_query(query: BaseQuery, filter: dict) -> BaseQuery:
	query = query_apply_common_filter(query, filter["accounts"], filter["partitions"], filter["states"])
	query = query_apply_date_filter(query, filter["date_from"], filter["date_to"])

	return query

def construct_full_table_query(query: BaseQuery, filter: dict) -> BaseQuery:
	query = construct_job_table_query(query, filter)

	query = query_apply_tags_filter(query, filter["req_tags"], filter["opt_tags"], filter["no_tags"])

	return query

from cachetools import cached, LRUCache
from cachetools.keys import hashkey

@cached(cache=LRUCache(32), key=lambda query_string, query: hashkey(query_string))
def calculate_job_query_stat(query_string: str, query: BaseQuery):
	jobs = list(query.all())

	result = {}

	result["cpu_h"] = sum(((job.t_end-job.t_start) * job.num_cores / 3600 for job,perf,tag in jobs))
	result["count"] = len(jobs)
	result["COMPLETED"] = sum((1 for job,perf,tag in jobs if job.state == "COMPLETED" or job.state == "COMPLETING"))
	result["CANCELLED"] = sum((1 for job,perf,tag in jobs if job.state == "CANCELLED"))
	result["TIMEOUT"] = sum((1 for job,perf,tag in jobs if job.state == "TIMEOUT"))
	result["FAILED"] = sum((1 for job,perf,tag in jobs if job.state == "FAILED"))
	result["NODE_FAIL"] = sum((1 for job,perf,tag in jobs if job.state == "NODE_FAIL"))

	return result

@job_table_api_pages.route("/common")
@crossdomain(origin='*')
def json_jobs_by_account() -> Response:
	data = construct_job_table_query(Job.query, request.args.to_dict()).all()

	return jsonify(list(map(lambda x: x.to_dict(), data)))
