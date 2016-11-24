import http.client

from flask import Blueprint, Response, jsonify, render_template, request

from application.database import global_db
from modules.autotag.models import AutoTag
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag, Tag

autotag_pages = Blueprint('autotag', __name__
	, template_folder='templates/', static_folder='static')

def apply_autotags(job: Job):
	perf = JobPerformance.query.get(job.id)
	job_tag = JobTag.query.get(job.id)

	for autotag in AutoTag.query.all():
		condition = autotag.compile_condition()

		try:
			if condition(job, perf):
				tag = Tag.query.get(autotag.fk_tag_id)
				job_tag.add(tag.label)
		except:
			pass

@autotag_pages.route("/list")
def autotag_list() -> Response:
	data = global_db.session.query(Tag, AutoTag).join(AutoTag).all()
	return render_template("autotag_list.html", data=data)
