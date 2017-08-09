from application.database import global_db
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.metrics.constants import METRIC_LIST

metric_columns = [
	global_db.Column("fk_job_id", global_db.Integer
		, global_db.ForeignKey("job.id")
		, primary_key=True)]

metric_type_map = {
	"float": global_db.Float,
	"int": global_db.Integer,
	"str": global_db.Text,
}

for metric, metric_type, _, _ in METRIC_LIST:
	metric_columns.append(global_db.Column(metric, metric_type_map[metric_type]))

class JobMetrics(global_db.Model):
	__table__ = global_db.Table("job_metric", *metric_columns)

	__table_args__ = ()

	def __init__(self, record_id: int):
		self.fk_job_id = record_id

	def to_dict(self) -> dict:
		result = {}

		for metric, _, _, _ in METRIC_LIST:
			result[metric] = getattr(self, metric)

		return result

	def update(self):
		job = Job.query.get(self.fk_job_id).to_dict()
		performance = JobPerformance.query.get(self.fk_job_id).to_dict()

		for metric, _, metric_func, _ in METRIC_LIST:
			try:
				self.__setattr__(metric, metric_func(job, performance))
			except:
				pass

		global_db.session.add(self)
		global_db.session.commit()

def calculate_metrics(job: Job):
	metrics = JobMetrics.query.get(job.id)
	metrics.update()
