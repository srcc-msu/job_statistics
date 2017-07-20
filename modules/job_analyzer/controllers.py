from functools import partial
import time
from typing import List

from flask import Blueprint, Response, render_template, current_app, request

from core.job.models import Job
from application.helpers import requires_auth
from core.monitoring.models import SENSOR_CLASS_MAP
from modules.job_table.helpers import get_color

job_analyzer_pages = Blueprint('job_analyzer', __name__
	, template_folder='templates/', static_folder='static')

def assign_job_class(data: dict) -> str:
	try:
		if int(data["stats"]["cpu"]["avg"]) < 10 and float(data["stats"]["la"]["avg"]) < 0.9:
			return "hanged"
		else:
			return "ok"
	except TypeError:
		return "no_data"

def get_running_stats(interval: int) -> List[dict]:
	jobs = Job.query.filter(Job.state.in_(current_app.app_config.cluster["ACTIVE_JOB_STATES"])).all()

	results = []

	timestamp = int(time.time())
	offset = current_app.app_config.monitoring["aggregation_interval"]

	for job in jobs:
		if timestamp - job.t_start < interval:
			continue

		data = {
			"stats" : {}
			, "job" : job.to_dict() # TODO: ???
		}

		nodelist = list(map(current_app.app_config.cluster["node2int"], job.expand_nodelist()))

		data["stats"]["cpu"] = SENSOR_CLASS_MAP["cpu_user"].get_stats(nodelist, timestamp - interval + offset, timestamp)
		data["stats"]["la"] = SENSOR_CLASS_MAP["loadavg"].get_stats(nodelist, timestamp - interval + offset, timestamp)

		data["class"] = assign_job_class(data)

		results.append(data)

	return results

@job_analyzer_pages.route("/running")
@requires_auth
def running_stats() -> Response:
	interval = int(request.args.get("interval", 60*60)) # last hour by default

	return render_template("running.html"
		, stats=get_running_stats(interval)
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
