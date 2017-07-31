from flask import Blueprint, Response, jsonify, request

from application.helpers import requires_auth
from modules.job_analyzer.controllers import get_running_stats

job_analyzer_api_pages = Blueprint('job_analyzer_api', __name__
	, template_folder='templates/', static_folder='static')

@job_analyzer_api_pages.route("/running")
@requires_auth
def running_stats() -> Response:
	interval = int(request.args.get("interval", 60*60)) # last hour by default
	return jsonify(get_running_stats(interval))
