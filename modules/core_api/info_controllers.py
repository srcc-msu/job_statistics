from flask import jsonify, Response, request, redirect, Blueprint

from core.job.models import Job
from application.helpers import crossdomain

job_info_api_pages = Blueprint('job_info_api', __name__
	, template_folder='templates')

@job_info_api_pages.route("/<int:record_id>")
@crossdomain(origin='*')
def json_job(record_id: int) -> Response:
	return redirect(request.base_url + "/info")

@job_info_api_pages.route("/<int:record_id>/info")
@crossdomain(origin='*')
def json_job_info(record_id: int) -> Response:
	data = Job.query.get_or_404(record_id)

	return jsonify(data.to_dict())
