from flask import jsonify, Response, request, Blueprint

from core.job.models import Job
from application.helpers import crossdomain
from core.tag.models import JobTag, Tag
from application.helpers import requires_auth

job_tag_api_pages= Blueprint('job_tag_api', __name__
	, template_folder='templates')

@job_tag_api_pages.route("/<int:record_id>/tags")
@crossdomain(origin='*')
def job_tags(record_id: int) -> Response:
	job =  Job.query.get_or_404(record_id)

	job_tag = JobTag.query.get(job.id)

	return jsonify(job_tag.to_dict())

@job_tag_api_pages.route("/<int:record_id>/tag/<string:tag>")
@crossdomain(origin='*')
def access_job_tag(record_id: int, tag: str) -> Response:
	"""GET = return tag stat, POST = create or delete and return tag stat"""
	job =  Job.query.get_or_404(record_id)

	return jsonify({"tag": tag, "job": record_id, "exist": check_job_tag(job, tag)})

@job_tag_api_pages.route("/<int:record_id>/tag/<string:tag>", methods=["POST"])
@requires_auth
def update_job_tag(record_id: int, tag: str) -> Response:
	"""GET = return tag stat, POST = create or delete and return tag stat"""
	job =  Job.query.get_or_404(record_id)

	if request.form["action"].lower() == "add":
		add_job_tag(job, tag)
	elif request.form["action"].lower() == "delete":
		delete_job_tag(job, tag)
	else:
		raise RuntimeError("unsupported tag operation: " + request.form["action"])

	return jsonify({"tag": tag, "job": record_id, "exist": check_job_tag(job, tag)})

def check_job_tag(job: Job, tag: str) -> bool:
	job_tag = JobTag.query.get(job.id)
	return job_tag.contains(tag)

def delete_job_tag(job: Job, tag: str):
	job_tag = JobTag.query.get(job.id)
	job_tag.delete(tag)

def add_job_tag(job: Job, tag: str) -> Response:
	_ = Tag.query.filter(Tag.label == tag).one() # check it is registered

	job_tag = JobTag.query.get(job.id)
	job_tag.add(tag)
