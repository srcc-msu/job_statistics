from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, Float

from core.job.models import Job
from core.monitoring.constants import SENSOR_LIST
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP

def update_performance(db: SQLAlchemy, job: Job) -> JobPerformance:
	data = {}

	for sensor in SENSOR_LIST:
		sensor_class = SENSOR_CLASS_MAP[sensor]

		offset = current_app.app_config.general["aggregation_interval"]

		filter_nodelist = list(map(current_app.app_config.cluster["node2int"], job.expand_nodelist()))

		query = db.session.query(
				func.min(sensor_class.min).cast(Float).label("min")
				, func.min(sensor_class.max).cast(Float).label("max")
				, func.avg(sensor_class.avg).cast(Float).label("avg"))\
			.filter(sensor_class.time > job.t_start + offset)\
			.filter(sensor_class.time < job.t_end - offset)\
			.filter(sensor_class.node_id.in_(filter_nodelist))\

		min, max, avg = query.one()

		data["min_" + sensor] = min
		data["max_" + sensor] = max
		data["avg_" + sensor] = avg

	query = JobPerformance.query.filter(JobPerformance.fk_job_id == job.id)
	query.update(data)
	db.session.commit()

	return query.one()

