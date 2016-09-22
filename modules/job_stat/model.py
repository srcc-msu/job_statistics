from flask import current_app
from sqlalchemy import Column, Integer, Table

from database import global_db

class JobStat(global_db.Model):
	TABLE_NAME = "job_stat"

	__table__ = Table(TABLE_NAME, global_db.metadata
		, Column('fk_job_id', Integer, global_db.ForeignKey("job.id"), primary_key=True)
		, autoload_with=global_db.get_engine(current_app), autoload=True)
