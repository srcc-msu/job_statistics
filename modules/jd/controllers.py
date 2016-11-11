from functools import partial

from flask import Blueprint, Response, render_template, request, current_app, redirect
from werkzeug.exceptions import abort

from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag
from core.job.helpers import id2hash, hash2id
from modules.job_table.helpers import get_color

jd_pages = Blueprint('jd', __name__
	, template_folder='templates', static_folder='static')

@jd_pages.route("/<int:job_id>")
def jd_redirect(job_id: int) -> Response:
	return redirect(request.base_url + "/0")

@jd_pages.route("/<int:job_id>/<int:task_id>")
def jd(job_id: int, task_id: int) -> Response:
	try:
		job = Job.get_by_id(job_id, task_id)
	except LookupError:
		abort(404)

	tag = JobTag.query.get(job.id)
	performance = JobPerformance.query.get(job.id)

	return render_template("jd.html", anon=False, id2hash=id2hash
		, job=job.to_dict(), tags=tag.to_dict(), monitoring=performance.to_dict()
		, derivative=current_app.app_config.monitoring["calculate_derivative"](performance.to_dict())
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))

@jd_pages.route("/share/<string:hash>")
def anon_jd(hash: str) -> Response:
	task_id = 0
	job_id = hash2id(hash)

	try:
		job = Job.get_by_id(job_id, task_id)
	except LookupError:
		abort(404)

	tag = JobTag.query.get(job.id)
	performance = JobPerformance.query.get(job.id)

	return render_template("jd.html", anon=True
		, job=job.to_dict(), tags=tag.to_dict(), monitoring=performance.to_dict()
		, derivative=current_app.app_config.monitoring["calculate_derivative"](performance.to_dict())
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
