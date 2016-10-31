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
	job_tags = JobTag.query.get(job.id)

	for autotag in AutoTag.query.all():
		condition = autotag.compile_condition()

		if condition(job, perf):
			tag = Tag.query.get(autotag.fk_tag_id)
			job_tags.add(tag.label)

@autotag_pages.route("/job/<int:record_id>", methods=["POST"])
def __apply_autotags(record_id: int) -> Response:
	job = Job.query.get(record_id)

	apply_autotags(job)

	return "", http.HTTPStatus.ACCEPTED

@autotag_pages.route("/list")
def autotag_list() -> Response:
	data = global_db.session.query(Tag, AutoTag).join(AutoTag).all()
	return render_template("autotag_list.html", data=data)

@autotag_pages.route("/tags/<string:label>", methods=["POST"])
def create_tag(label: str) -> Response:
	tag = Tag(label, request.form["description"])

	global_db.session.add(tag)
	global_db.session.commit()

	return jsonify({"tag" : label, "description": request.form["description"]})