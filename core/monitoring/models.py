from application.database import global_db

from core.monitoring.constants import SENSOR_LIST

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
#

class Sensor(global_db.Model):
	__abstract__ = True

	time = global_db.Column("time", global_db.Integer, primary_key=True)
	node_id = global_db.Column("node_id", global_db.Integer, primary_key=True)
	min = global_db.Column("min", global_db.Float)
	max = global_db.Column("max", global_db.Float)
	avg = global_db.Column("avg", global_db.Float)


SENSOR_CLASS_MAP = {}

for name in SENSOR_LIST:
	SENSOR_CLASS_MAP[name] = type(name, (Sensor,),{"__tablename__": "sensor_" + name})
