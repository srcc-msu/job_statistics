from typing import List

from sqlalchemy import func, Float

from application.database import global_db
from core.job.models import Job
from core.monitoring.constants import SENSOR_LIST
from core.monitoring.helpers import nodelist2ids

perf_columns = [
	global_db.Column("fk_job_id", global_db.Integer
		, global_db.ForeignKey("job.id")
		, primary_key=True)]

for sensor in SENSOR_LIST:
	perf_columns.append(global_db.Column("min_" + sensor, global_db.Float))
	perf_columns.append(global_db.Column("max_" + sensor, global_db.Float))
	perf_columns.append(global_db.Column("avg_" + sensor, global_db.Float))

class JobPerformance(global_db.Model):
	__table__ = global_db.Table("job_performance", *perf_columns)

	__table_args__ = ()

	def __init__(self, record_id: int):
		self.fk_job_id = record_id

	def to_dict(self) -> dict:
		result = {"min": {}, "max": {}, "avg": {}}

		for sensor_name in SENSOR_LIST:
			result["min"][sensor_name] = getattr(self, "min_" + sensor_name)
			result["max"][sensor_name] = getattr(self, "max_" + sensor_name)
			result["avg"][sensor_name] = getattr(self, "avg_" + sensor_name)

		return result

	def update(self, offset: int):
		job = Job.query.get(self.fk_job_id)

		for sensor in SENSOR_LIST:
			stats = SENSOR_CLASS_MAP[sensor].get_stats(job.expanded_nodelist, job.t_start + offset, job.t_end)

			self.__setattr__("min_" + sensor, stats["min"])
			self.__setattr__("max_" + sensor, stats["max"])
			self.__setattr__("avg_" + sensor, stats["avg"])

		global_db.session.add(self)
		global_db.session.commit()

class Sensor(global_db.Model):
	__abstract__ = True

	time = global_db.Column("time", global_db.Integer, primary_key=True)
	node_id = global_db.Column("node_id", global_db.Integer, primary_key=True)
	min = global_db.Column("min", global_db.Float)
	max = global_db.Column("max", global_db.Float)
	avg = global_db.Column("avg", global_db.Float)

	@classmethod
	def get_stats(cls, nodelist: List[str], t_from : int, t_to: int):
		id_list = nodelist2ids(nodelist)

		query = (global_db.session.query(
				func.min(cls.min).cast(Float).label("min")
				, func.max(cls.max).cast(Float).label("max")
				, func.avg(cls.avg).cast(Float).label("avg"))
			.filter(cls.time > t_from)
			.filter(cls.time < t_to)
			.filter(cls.node_id.in_(id_list)))

		result = query.one()

		return {
			"min" : result[0]
			, "max" : result[1]
			, "avg" : result[2]
		}

	@classmethod
	def get_raw(cls, nodelist: List[str], t_from : int, t_to: int):
		id_list = nodelist2ids(nodelist)

		query = (global_db.session.query(
			cls.time
				, func.min(cls.min).cast(Float).label("min")
				, func.max(cls.max).cast(Float).label("max")
				, func.avg(cls.min).cast(Float).label("avg_min")
				, func.avg(cls.max).cast(Float).label("avg_max")
				, func.avg(cls.avg).cast(Float).label("avg"))
			.filter(cls.time > t_from)
			.filter(cls.time < t_to)
			.filter(cls.node_id.in_(id_list))
			.group_by(cls.time)
			.order_by(cls.time))

		return list(query.all())

	@classmethod
	def get_heatmap(cls, nodelist: List[str], t_from : int, t_to: int):
		id_list = nodelist2ids(nodelist)

		query = (global_db.session.query(
				cls.time
				, cls.node_id
				, cls.min
				, cls.max
				, cls.avg)
			.filter(cls.time > t_from)
			.filter(cls.time < t_to)
			.filter(cls.node_id.in_(id_list)))

		return list(query.all())



SENSOR_CLASS_MAP = {}

for name in SENSOR_LIST:
	SENSOR_CLASS_MAP[name] = type(name, (Sensor,), {"__tablename__": "sensor_" + name})
