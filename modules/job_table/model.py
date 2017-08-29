from typing import List, Optional

from flask import current_app
from flask import Blueprint
from flask_sqlalchemy import BaseQuery
from sqlalchemy import or_

from core.job.models import Job
from core.tag.models import JobTag

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

	result = {
		"count" : len(jobs)
		, "cpu_h" : 0
		, "state" : {}
		, "perf" : {"avg" : {}}
	}

	states = current_app.app_config.cluster["JOB_STATES"]
	sensors = current_app.app_config.monitoring["SENSOR_LIST"]

	for state in states:
		result["state"][state] = 0

	for sensor in sensors:
		result["perf"]["avg"]["avg_" + sensor] = 0

	if len(jobs) == 0:
		return result

	perf_count = 0

	for job,tag,perf in jobs:
		result["cpu_h"] += (job.t_end-job.t_start) * job.num_cores / 3600

		result["state"][job.state] += 1

		has_perf_metric = False

		for sensor in sensors:
			try:
				result["perf"]["avg"]["avg_" + sensor] += getattr(perf, "avg_" + sensor)
			except:
				pass
			else:
				has_perf_metric = True

		if has_perf_metric:
			perf_count += 1

#		except Exception as e:
#			print("error calculating stat for {0}, skipped".format(job.id), file=sys.stderr)
#			print(e)

	if perf_count > 0:
		for sensor in sensors:
			result["perf"]["avg"]["avg_" + sensor] = result["perf"]["avg"].get("avg_" + sensor, 0) / perf_count

	return result

