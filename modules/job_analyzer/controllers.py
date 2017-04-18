from functools import partial
from flask import Blueprint, Response, render_template, request, Flask, current_app
import time

from application.database import global_db
from core.monitoring.controllers import get_sensor_stats
from core.job.models import Job
from application.helpers import requires_auth
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
			cpu_stat = get_sensor_stats(global_db, "cpu_user", nodelist, timestamp - limit + offset, timestamp)
			la_stat =  get_sensor_stats(global_db, "loadavg", nodelist, timestamp - limit + offset, timestamp)

			try:
				if int(cpu_stat[2]) < 10 and int(la_stat[2]) < 0.9:
					results.insert(0, (job, cpu_stat, la_stat, "HANGED?!"))
				else:
					results.append((job, cpu_stat, la_stat, ""))
			except TypeError:
				results.append((job, cpu_stat, la_stat, "no data"))

	return results

@job_analyzer_pages.route("/running")
@requires_auth
def autotag_list() -> Response:
	return render_template("running.html"
		, stats=get_running_stats(60*60)
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
