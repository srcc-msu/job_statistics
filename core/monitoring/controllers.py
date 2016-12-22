import threading
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, Float

from core.job.models import Job
from core.monitoring.constants import SENSOR_LIST
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP

def __update_performance(app: Flask, db: SQLAlchemy, job: Job, offset, node2int) -> JobPerformance:
	with app.app_context():
		data = {}

		for sensor in SENSOR_LIST:
			sensor_class = SENSOR_CLASS_MAP[sensor]

			filter_nodelist = list(map(node2int, job.expand_nodelist()))

			query = db.session.query(
					func.min(sensor_class.min).cast(Float).label("min")
					, func.max(sensor_class.max).cast(Float).label("max")
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

def update_performance(app: Flask, db: SQLAlchemy, job: Job) -> JobPerformance:
	"""TODO: move to RQ"""
	thread = threading.Thread(target=__update_performance, args=(app, db, job
		, app.app_config.general["aggregation_interval"], app.app_config.cluster["node2int"]))
	thread.daemon = True
	thread.start()
