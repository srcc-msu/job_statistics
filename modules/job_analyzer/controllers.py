from functools import partial
import time

from flask import Blueprint, Response, render_template, current_app, request

from core.job.models import Job
from application.helpers import requires_auth
from core.monitoring.models import SENSOR_CLASS_MAP
from modules.job_table.helpers import get_color

job_analyzer_pages = Blueprint('job_analyzer', __name__
	, template_folder='templates/', static_folder='static')

def get_running_stats(limit: int):
	jobs = Job.query.filter(Job.state == "RUNNING").all()

	results = []

	timestamp = int(time.time())
	offset = current_app.app_config.monitoring["aggregation_interval"]

	for job in jobs:
		nodelist = list(map(current_app.app_config.cluster["node2int"], job.expand_nodelist()))
		if timestamp - job.t_start > limit:
			cpu_stat = SENSOR_CLASS_MAP["cpu_user"].get_stats(nodelist, timestamp - limit + offset, timestamp)
			la_stat =  SENSOR_CLASS_MAP["loadavg"].get_stats(nodelist, timestamp - limit + offset, timestamp)

			try:
				if int(cpu_stat["avg"]) < 10 and float(la_stat["avg"]) < 0.9:
					results.insert(0, (job, cpu_stat, la_stat, "HANGED?!"))
				else:
					results.append((job, cpu_stat, la_stat, ""))
			except TypeError:
				results.append((job, cpu_stat, la_stat, "no data"))

	return results

@job_analyzer_pages.route("/running")
@requires_auth
def running_stats() -> Response:
	interval = int(request.args.get("interval", 60*60)) # last hour by default

	return render_template("running.html"
		, stats=get_running_stats(interval)
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
