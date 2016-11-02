from application.database import global_db

from core.monitoring.constants import SENSOR_MAP

perf_columns = [
	global_db.Column("fk_job_id", global_db.Integer
		, global_db.ForeignKey("job.id")
		, primary_key=True)]

for sensor in SENSOR_MAP.values():
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

		sensor_list = ["cpu_user", "cpu_system"
			, "cpu_flops", "cpu_perf_l1d_repl", "llc_miss"
			, "mem_load", "mem_store"
			, "ib_rcv_data", "ib_xmit_data"
			, "loadavg", "gpu_load"]

		for sensor_name in sensor_list:
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

class Sensor_bytes_in(Sensor):
	__tablename__ = "bytes_in"

class Sensor_bytes_out(Sensor):
	__tablename__ = "bytes_out"

class Sensor_llc_miss(Sensor):
	__tablename__ = "llc_miss"

class Sensor_cpu_perf_l1d_repl(Sensor):
	__tablename__ = "cpu_perf_l1d_repl"

class Sensor_cpu_flops(Sensor):
	__tablename__ = "cpu_flops"

class Sensor_mem_load(Sensor):
	__tablename__ = "mem_load"

class Sensor_mem_store(Sensor):
	__tablename__ = "mem_store"

class Sensor_cpu_user(Sensor):
	__tablename__ = "cpu_user"

class Sensor_cpu_nice(Sensor):
	__tablename__ = "cpu_nice"

class Sensor_cpu_system(Sensor):
	__tablename__ = "cpu_system"

class Sensor_cpu_idle(Sensor):
	__tablename__ = "cpu_idle"

class Sensor_cpu_iowait(Sensor):
	__tablename__ = "cpu_iowait"

class Sensor_cpu_irq(Sensor):
	__tablename__ = "cpu_irq"

class Sensor_cpu_soft_irq(Sensor):
	__tablename__ = "cpu_soft_irq"

class Sensor_disk_bytes_in(Sensor):
	__tablename__ = "disk_bytes_in"

class Sensor_disk_bytes_out(Sensor):
	__tablename__ = "disk_bytes_out"

class Sensor_disk_ops_in(Sensor):
	__tablename__ = "disk_ops_in"

class Sensor_disk_ops_out(Sensor):
	__tablename__ = "disk_ops_out"

class Sensor_ib_rcv_data(Sensor):
	__tablename__ = "ib_rcv_data"

class Sensor_ib_xmit_data(Sensor):
	__tablename__ = "ib_xmit_data"

class Sensor_ib_rcv_pckts(Sensor):
	__tablename__ = "ib_rcv_pckts"

class Sensor_ib_xmit_pckts(Sensor):
	__tablename__ = "ib_xmit_pckts"

class Sensor_gpu_mem_usage(Sensor):
	__tablename__ = "gpu_mem_usage"

class Sensor_gpu_load(Sensor):
	__tablename__ = "gpu_load"

class Sensor_gpu_mem_load(Sensor):
	__tablename__ = "gpu_mem_load"

class Sensor_loadavg(Sensor):
	__tablename__ = "loadavg"

class Sensor_pkts_in(Sensor):
	__tablename__ = "pkts_in"

class Sensor_pkts_out(Sensor):
	__tablename__ = "pkts_out"

class Sensor_swapping_in(Sensor):
	__tablename__ = "swapping_in"

class Sensor_swapping_out(Sensor):
	__tablename__ = "swapping_out"
