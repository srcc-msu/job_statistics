from flask import jsonify, Response, Blueprint

from core.job.models import Job
from application.helpers import crossdomain
from core.metrics.models import JobMetrics

job_metrics_api_pages = Blueprint('job_metrics_api', __name__
	, template_folder='templates')

@job_metrics_api_pages.route("/<int:record_id>/metrics")
@crossdomain(origin='*')
def json_job_metric(record_id: int) -> Response:
	_ = Job.query.get_or_404(record_id)
	metrics = JobMetrics.query.get(record_id)

	return jsonify(metrics.to_dict())
