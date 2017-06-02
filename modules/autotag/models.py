from typing import Callable

from application.database import global_db
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag, Tag

class AutoTag(global_db.Model):
	__tablename__ = 'autotag'

	id = global_db.Column(global_db.Integer, primary_key=True, index=True)  # inner entry id

	fk_tag_id = global_db.Column("fk_tag_id", global_db.Integer
		, global_db.ForeignKey("tag.id"))

	condition = global_db.Column(global_db.Text)

	def __init__(self, record_id: int, condition: str):
		self.fk_tag_id = record_id
		self.condition = condition

	def compile_condition(self) -> Callable[[Job, JobPerformance], bool]:
		"""eval is safe here - condition can not be create by users"""

		return eval("lambda job, perf: " + self.condition)

def apply_autotags(job: Job):
	perf = JobPerformance.query.get(job.id)
	job_tag = JobTag.query.get(job.id)

	for autotag in AutoTag.query.all():
		condition = autotag.compile_condition()

		try:
			tag = Tag.query.get(autotag.fk_tag_id)

			if condition(job, perf):
				job_tag.add(tag.label)
			else:
				job_tag.delete(tag.label)

		except:
			pass
