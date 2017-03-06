from flask import Blueprint, Response, render_template, request, Flask, current_app
import time

from application.database import global_db
from application.helpers import background
from modules.autotag.models import AutoTag
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag, Tag
from application.helpers import requires_auth

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
@requires_auth
def autotag_list() -> Response:
	data = global_db.session.query(Tag, AutoTag).join(AutoTag).all()
	return render_template("autotag_list.html", data=data)

def __apply_since(app: Flask, since: int):
	with app.app_context():
		jobs = Job.query.filter(Job.t_end > since).all()

		for job in jobs:
			apply_autotags(job)

		print("updated {0} since {1}".format(len(jobs), since))

@autotag_pages.route("/apply", methods=["POST"])
@requires_auth
def apply_since() -> Response:
	since = int(request.args.get("since", int(time.time()) - 60*60)) # last hour by default

	background(__apply_since, (current_app._get_current_object(), since))

	return "ok"
