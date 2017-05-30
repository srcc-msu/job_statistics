from functools import partial
import time

from flask import Blueprint, Response, render_template, current_app, jsonify, request

from core.job.models import Job
from application.helpers import requires_auth
from core.monitoring.models import SENSOR_CLASS_MAP
from modules.job_analyzer.controllers import get_running_stats
from modules.job_table.helpers import get_color

job_analyzer_api_pages = Blueprint('job_analyzer_api', __name__
	, template_folder='templates/', static_folder='static')

@job_analyzer_api_pages.route("/running")
@requires_auth
def running_stats() -> Response:
	interval = int(request.args.get("interval", 60*60)) # last hour by default
	return jsonify(get_running_stats(interval))
