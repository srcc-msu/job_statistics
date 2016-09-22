from flask_sqlalchemy import SQLAlchemy

from core.job.models import Job
from core.tag.models import JobTag
from core.monitoring.models import JobPerformance

def __add_perf(db: SQLAlchemy, perf: JobPerformance):
	db.session.add(perf)
	db.session.commit()

def __add_tag(db: SQLAlchemy, tag: JobTag):
	db.session.add(tag)
	db.session.commit()

def add(db: SQLAlchemy, job: Job):
	db.session.add(job)
	db.session.commit()

	__add_perf(db, JobPerformance(job.id))
	__add_tag(db, JobTag(job.id))

def add_or_update(db: SQLAlchemy, job_info: dict) -> Job:
	job_query = Job.query.filter(Job.job_id == job_info["job_id"]).filter(Job.task_id == job_info["task_id"])
	job = job_query.scalar()

	if job is None:
		job = Job(**job_info)
		add(db, job)

		return job
	else:
		if job.state == "RUNNING":
			job_query.update(job_info)
			db.session.commit()

			return job
		else:
			raise RuntimeError("job already exists")
