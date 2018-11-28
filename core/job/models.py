import sqlalchemy
from typing import List

from application.database import global_db
from core.job.helpers import expand_nodelist


class Job(global_db.Model):
	__tablename__ = 'job'

	__table_args__ = (
		global_db.Index('job_index', "job_id", "task_id")
		, global_db.UniqueConstraint('job_id', 'task_id', name='unique_jobs')
		, global_db.CheckConstraint("t_submit > 0", name="good_submit")
		, global_db.CheckConstraint("t_start >= t_submit", name="good_start")
		, global_db.CheckConstraint("t_end >= t_start", name="good_end")
		, global_db.CheckConstraint("t_end - t_start < 60*60*24*14", name="good_length"))

	id = global_db.Column("id", global_db.Integer, primary_key=True)  # inner entry id

	job_id = global_db.Column(global_db.Integer, index=True)  # scheduler id
	task_id = global_db.Column(global_db.Integer, default=0)  # scheduler sub-id for stupid job with same id

	partition = global_db.Column(global_db.String(64))
	account = global_db.Column(global_db.String(64))

	t_submit = global_db.Column(global_db.Integer)
	t_start = global_db.Column(global_db.Integer)
	t_end = global_db.Column(global_db.Integer)
	timelimit = global_db.Column(global_db.Integer)

	num_nodes = global_db.Column(global_db.Integer)
	num_cores = global_db.Column(global_db.Integer)
	state = global_db.Column(global_db.String(16))
	priority = global_db.Column(global_db.BigInteger)

	command = global_db.Column(global_db.Text())
	workdir = global_db.Column(global_db.Text())
	nodelist = global_db.Column(global_db.Text())

	@property
	def expanded_nodelist(self) -> List[str]:
		return expand_nodelist(self.nodelist)

	def __init__(self, job_id: int, task_id: int, partition: str, account: str
			, t_submit: int, t_start: int, t_end: int, timelimit: int
			, num_nodes: int, num_cores: int, state: str, priority: int
			, command: str, workdir: str, nodelist: str):
		self.job_id = job_id
		self.task_id = task_id

		self.partition = partition
		self.account = account

		self.t_submit = t_submit
		self.t_start = t_start
		self.t_end = t_end
		self.timelimit = timelimit

		self.num_nodes = num_nodes
		self.num_cores = num_cores
		self.state = state
		self.priority = priority

		self.command = command
		self.workdir = workdir
		self.nodelist = nodelist

	def __repr__(self) -> str:
		return "<job_id {}>".format(self.job_id)

	def to_dict(self) -> dict:
		return {
			"id": self.id
			, "job_id": self.job_id
			, "task_id": self.task_id

			, "partition": self.partition
			, "account": self.account

			, "t_submit": self.t_submit
			, "t_start": self.t_start
			, "t_end": self.t_end
			, "timelimit": self.timelimit

			, "num_nodes": self.num_nodes
			, "num_cores": self.num_cores
			, "state": self.state
			, "priority": self.priority

			, "command": self.command
			, "workdir": self.workdir
			, "nodelist": self.nodelist}

	@staticmethod
	def get_by_id(job_id: int, task_id: int):
		try:
			return Job.query.filter(Job.job_id == job_id).filter(Job.task_id == task_id).one()
		except sqlalchemy.orm.exc.NoResultFound as e:
			raise LookupError("job not found") from e
