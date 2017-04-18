from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, Float

from core.job.models import Job
from core.monitoring.constants import SENSOR_LIST
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP
from application.helpers import background

def get_sensor_stats(db: SQLAlchemy, sensor: str, nodelist: str, t_from : int, t_to: int):
	sensor_class = SENSOR_CLASS_MAP[sensor]

	sensor_query = db.session.query(
			func.min(sensor_class.min).cast(Float).label("min")
			, func.max(sensor_class.max).cast(Float).label("max")
			, func.avg(sensor_class.avg).cast(Float).label("avg"))\
		.filter(sensor_class.time > t_from)\
		.filter(sensor_class.time < t_to)\
		.filter(sensor_class.node_id.in_(nodelist))\

	return sensor_query.one()


def __update_performance(app: Flask, db: SQLAlchemy, job: Job, force: bool):
	with app.app_context():
		offset = app.app_config.monitoring["aggregation_interval"]
		filter_nodelist = list(map(app.app_config.cluster["node2int"], job.expand_nodelist()))

		data = {}

		query = JobPerformance.query.filter(JobPerformance.fk_job_id == job.id)
		current_perf = query.one().to_dict()

		for sensor in SENSOR_LIST:
			if force \
				or current_perf["min"].get(sensor, None) is None \
				or current_perf["max"].get(sensor, None) is None \
				or current_perf["avg"].get(sensor, None) is None:
				pass
			else:
				continue

			min, max, avg = get_sensor_stats(db, sensor, filter_nodelist, job.t_start + offset, job.t_end - offset)

			data["min_" + sensor] = min
			data["max_" + sensor] = max
			data["avg_" + sensor] = avg

		if len(data) == 0:
			return

		query.update(data)
		db.session.commit()

def update_performance(app: Flask, db: SQLAlchemy, job: Job, force: bool):
	background(__update_performance, (app, db, job, force))
