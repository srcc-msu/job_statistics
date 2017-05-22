from flask import jsonify, request
from flask import Blueprint, Response

from core.job.models import Job
from application.helpers import crossdomain
from modules.job_table.model import construct_job_table_query

job_table_api_pages = Blueprint('job_table_api', __name__
	, template_folder='templates')


@job_table_api_pages.route("/common")
@crossdomain(origin='*')
def json_jobs_by_account() -> Response:
	data = construct_job_table_query(Job.query, request.args.to_dict()).all()

	return jsonify(list(map(lambda x: x.to_dict(), data)))
