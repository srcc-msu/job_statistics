from flask import jsonify, Response, current_app, Blueprint
from sqlalchemy import func, Float

from application.database import global_db
from core.job.models import Job
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP
from application.helpers import crossdomain
from modules.core_api.helpers import shrinked

job_monitoring_api_pages= Blueprint('job_monitoring_api', __name__
	, template_folder='templates')

@job_monitoring_api_pages.route("/<int:record_id>/performance")
@crossdomain(origin='*')
def json_job_performance(record_id: int) -> Response:
	_ = Job.query.get_or_404(record_id)
	data = JobPerformance.query.get(record_id)

	return jsonify(data.to_dict())

SHRINK_THRESHOLD = 500

@job_monitoring_api_pages.route("/<int:record_id>/sensor/<string:sensor>", defaults={'shrink': SHRINK_THRESHOLD})
@job_monitoring_api_pages.route("/<int:record_id>/sensor/<string:sensor>/<int:shrink>")
@crossdomain(origin='*')
def job_sensor(sensor: str, record_id: int, shrink: int) -> Response:

	job = Job.query.get(record_id)

	sensor_class = SENSOR_CLASS_MAP[sensor]

	offset = current_app.app_config.monitoring["aggregation_interval"]

	data = sensor_class.get_raw(job.expanded_nodelist, job.t_start + offset, job.t_end)

	if len(data) < shrink:
		result = []

		for entry in data:
			result.append({
				"time": entry[0]
				, "min" : entry[1]
				, "max" : entry[2]
				, "avg_min" : entry[3]
				, "avg_max" : entry[4]
				, "avg" : entry[5]
			})
		return jsonify(result)

	else:
		return jsonify(shrinked(data, shrink))

