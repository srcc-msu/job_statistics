from flask import jsonify, Response, current_app, Blueprint
from sqlalchemy import func, Float

from application.database import global_db
from core.job.helpers import expand_nodelist
from core.job.models import Job
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP
from application.helpers import crossdomain

job_monitoring_api_pages= Blueprint('job_monitoring_api', __name__
	, template_folder='templates')

@job_monitoring_api_pages.route("/<int:record_id>/performance")
@crossdomain(origin='*')
def json_job_performance(record_id: int) -> Response:
	_ = Job.query.get_or_404(record_id)
	data = JobPerformance.query.get(record_id)

	return jsonify(data.to_dict())

def shrinked(data, shrink_threshold):
	result = []

	factor = len(data) // shrink_threshold

	chunks = (data[x:x+factor] for x in range(0, len(data), factor))
	for chunk in chunks:
		l = len(chunk)

		result.append({
			"time": chunk[0][0]
			, "min" : min((x[1] for x in chunk))
			, "max" : max((x[2] for x in chunk))
			, "avg_min" : sum((x[3] for x in chunk)) / l
			, "avg_max" : sum((x[4] for x in chunk)) / l
			, "avg" : sum((x[5] for x in chunk)) / l
		})

	return result

SHRINK_THRESHOLD = 500

@job_monitoring_api_pages.route("/<int:record_id>/sensor/<string:sensor>", defaults={'shrink': SHRINK_THRESHOLD})
@job_monitoring_api_pages.route("/<int:record_id>/sensor/<string:sensor>/<int:shrink>")
@crossdomain(origin='*')
def job_sensor(sensor: str, record_id: int, shrink: int) -> Response:

	job = Job.query.get(record_id)

	sensor_class = SENSOR_CLASS_MAP[sensor]

	offset = current_app.app_config.monitoring["aggregation_interval"]

	filter_nodelist = list(map(current_app.app_config.cluster["node2int"], expand_nodelist(job.nodelist)))

	query = global_db.session.query(
		sensor_class.time
			, func.min(sensor_class.min).cast(Float).label("min")
			, func.max(sensor_class.max).cast(Float).label("max")
			, func.avg(sensor_class.min).cast(Float).label("avg_min")
			, func.avg(sensor_class.max).cast(Float).label("avg_max")
			, func.avg(sensor_class.avg).cast(Float).label("avg"))\
		.filter(sensor_class.time > job.t_start + offset)\
		.filter(sensor_class.time < job.t_end - offset)\
		.filter(sensor_class.node_id.in_(filter_nodelist))\
		.group_by(sensor_class.time)\
		.order_by(sensor_class.time)

	data = query.all()

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

