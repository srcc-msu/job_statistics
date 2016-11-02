from functools import partial

from flask import Blueprint, Response, render_template, request, current_app, redirect
from werkzeug.exceptions import abort

from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag
from modules.job_table.helpers import get_color

jd_pages = Blueprint('jd', __name__
	, template_folder='templates', static_folder='static')

@jd_pages.route("/<int:job_id>")
def jd_redirect(job_id: int) -> Response:
	return redirect(request.base_url + "/0")

def calculate_derivative(monitoring: dict):
	derivative = {}

	try:
		derivative["mem_l1_ratio"] = \
			(monitoring["avg"]["mem_load"] + monitoring["avg"]["mem_store"]) / monitoring["avg"]["cpu_perf_l1d_repl"]
	except:
		pass

	try:
		derivative["l1_l3_ratio"] = \
			monitoring["avg"]["cpu_perf_l1d_repl"] / monitoring["avg"]["llc_miss"]
	except:
		pass

	try:
		derivative["ib_rcv_pckt_size"] = \
			monitoring["avg"]["ib_rcv_data"] / monitoring["avg"]["ib_rcv_pckts"]
	except:
		pass

	try:
		derivative["ib_xmt_pckt_size"] = \
			monitoring["avg"]["ib_xmit_data"] / monitoring["avg"]["ib_xmit_pckts"]
	except:
		pass

	try:
		derivative["ib_rcv_pckt_size2"] = \
			monitoring["avg"]["ib_rcv_data2"] / monitoring["avg"]["ib_rcv_pckts2"]
	except:
		pass

	try:
		derivative["ib_xmt_pckt_size2"] = \
			monitoring["avg"]["ib_xmit_data2"] / monitoring["avg"]["ib_xmit_pckts2"]
	except:
		pass

	return derivative

@jd_pages.route("/<int:job_id>/<int:task_id>")
def jd(job_id: int, task_id: int) -> Response:
	try:
		job = Job.get_by_id(job_id, task_id)
	except LookupError:
		abort(404)

	tag = JobTag.query.get(job.id)
	performance = JobPerformance.query.get(job.id)

	return render_template("jd.html"
		, job=job.to_dict(), tags=tag.to_dict(), monitoring=performance.to_dict()
		, derivative=calculate_derivative(performance.to_dict())
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
