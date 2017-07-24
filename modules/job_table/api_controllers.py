from flask import jsonify, request
from flask import Blueprint, Response

from core.job.models import Job
from application.helpers import crossdomain
from modules.job_table.controllers import get_job_table_filter
from modules.job_table.model import construct_job_table_query, query_apply_tags_filter

job_table_api_pages = Blueprint('job_table_api', __name__
	, template_folder='templates')


@job_table_api_pages.route("/common")
@crossdomain(origin='*')
def json_jobs_by_account() -> Response:
	filter = get_job_table_filter()

	query = construct_job_table_query(Job.query, filter)
	query = query_apply_tags_filter(query, filter["req_tags"], filter["opt_tags"], filter["no_tags"])

	data = query.all()

	return jsonify(list(map(lambda x: x.to_dict(), data)))
