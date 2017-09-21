from flask import Blueprint, Response, request, jsonify
from sqlalchemy import func
from application.database import global_db

from application.helpers import crossdomain
from core.job.models import Job
from core.tag.models import JobTag
from modules.job_stat.controllers import generate_query
import application

job_stat_api_pages = Blueprint('job_stat_api', __name__
	, template_folder='templates', static_folder='static')

@job_stat_api_pages.route("/metric/<string:metric>/<string:aggregation_function>")
@job_stat_api_pages.route("/<string:metric>/<string:aggregation_function>") #TODO? legacy support
@crossdomain(origin='*')
def get_metric(metric: str, aggregation_function: str) -> Response:

	if aggregation_function not in ["min", "max", "avg", "count", "sum"]:
		raise RuntimeError("bad aggregation function: " + aggregation_function)

	result = generate_query(request.args, metric, aggregation_function)

	return application.helpers.gen_csv_response(result.column_descriptions, result.all())

@job_stat_api_pages.route("/tag/<string:tag>")
@crossdomain(origin='*')
def get_tag_stat(tag: str):
	t_from = request.args["t_from"]
	t_to = request.args["t_to"]

	query = (global_db.session.query(Job.account, func.count(Job.id)).join(JobTag)
		.filter(Job.t_end > t_from)
		.filter(Job.t_end < t_to)
		.filter(JobTag.tags.like("%{0}%".format(tag)))
		.group_by(Job.account))

	result = []
	for entry in query.all():
		result.append([entry[0], entry[1]])

	return jsonify(result)
