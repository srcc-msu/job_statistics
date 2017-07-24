from flask import Blueprint, Response, jsonify

from application.helpers import crossdomain
from modules.job_table.controllers import get_job_table_filter, get_job_table_query

job_table_api_pages = Blueprint('job_table_api', __name__
	, template_folder='templates')


@job_table_api_pages.route("/common")
@crossdomain(origin='*')
def json_jobs_by_account() -> Response:
	filter = get_job_table_filter()

	query = get_job_table_query(filter)

	return jsonify(list(map(lambda x: x[0].to_dict(), query.all())))
