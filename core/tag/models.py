from typing import Iterable, List

from application.database import global_db
from core.tag.constants import TAG_SEPARATOR

class JobTag(global_db.Model):
	__tablename__ = 'job_tag'

	fk_job_id = global_db.Column("fk_job_id", global_db.Integer
		, global_db.ForeignKey("job.id")
		, primary_key=True)

	tags = global_db.Column(global_db.Text)

	def __init__(self, record_id: int):
		self.fk_job_id = record_id
		self.tags = ""

	def to_dict(self) -> dict:
		return {
			"job": self.fk_job_id
			, "tags": self.get()}

	def __set(self, tags: Iterable[str]):
		self.tags = TAG_SEPARATOR + TAG_SEPARATOR.join(set(tags)) + TAG_SEPARATOR

		global_db.session.commit()

	def get(self) -> List[str]:
		if len(self.tags) == 0:
			return []

		return list(filter(lambda x: len(x) > 0, self.tags.split(TAG_SEPARATOR)))

	def add(self, tag: str):
		if TAG_SEPARATOR in tag:
			raise RuntimeError("bad tag name: ", tag)
		self.__set(self.get() + [tag])

	def delete(self, tag: str):
		tags = self.get()

		try:
			tags.remove(tag)
		except ValueError:
			return

		self.__set(tags)

	def contains(self, tag: str) -> bool:
		return tag in self.get()

	@staticmethod
	def by_jobs(jobs: Iterable[dict]) -> Iterable[dict]:
		ids = [entry["id"] for entry in jobs]
		query = JobTag.query.filter(JobTag.id.in_(ids))
		result = [tag.to_dict() for tag in query.all()]

		return result

class Tag(global_db.Model):
	MAX_TAG_LENGTH = 32

	__tablename__ = 'tag'

	id = global_db.Column(global_db.Integer, primary_key=True, index=True)

	label = global_db.Column(global_db.String(MAX_TAG_LENGTH), unique=True, index=True, nullable=False)
	description = global_db.Column(global_db.Text())

	def __init__(self, label, description):
		self.label = label
		self.description = description
