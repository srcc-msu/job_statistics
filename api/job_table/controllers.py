from typing import List, Optional

from flask import jsonify, request
from flask import Blueprint, Response
from flask_sqlalchemy import BaseQuery
from sqlalchemy import or_

from core.job.models import Job
from core.tag.models import JobTag

job_table_api_pages = Blueprint('job_table_api', __name__
	, template_folder='templates')

def extract_string_list(request: dict, field_name: str):
	result = request.get(field_name, "")

	if len(result) == 0:
		return []

	return result.split(",")

def extract_number(request: dict, field_name: str, default = None):
	result = request.get(field_name)

	try:
		return int(result)
	except (ValueError, TypeError):
		return default

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
		query = query.filter(Job.t_start > date_from)

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

def construct_job_table_query(query: BaseQuery, params: dict) -> BaseQuery:
	accounts = extract_string_list(params, "accounts")
	partitions = extract_string_list(params, "partitions")
	states = extract_string_list(params, "states")

	date_from = extract_number(params, "date_from", None)
	date_to = extract_number(params, "date_to", None)

	query = query_apply_common_filter(query, accounts, partitions, states)
	query = query_apply_date_filter(query, date_from, date_to)

	return query

def construct_full_table_query(query: BaseQuery, params: dict) -> BaseQuery:
	query = construct_job_table_query(query, params)

	req_tags = extract_string_list(params, "req_tags")
	opt_tags = extract_string_list(params, "opt_tags")
	no_tags = extract_string_list(params, "no_tags")

	query = query_apply_tags_filter(query, req_tags, opt_tags, no_tags)

	return query

@job_table_api_pages.route("/common")
def json_jobs_by_account() -> Response:
	data = construct_job_table_query(Job.query, request.args.to_dict()).all()

	return jsonify(list(map(lambda x: x.to_dict(), data)))
