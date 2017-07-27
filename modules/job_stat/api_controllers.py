from flask import Blueprint, Response, request

from application.helpers import crossdomain
from modules.job_stat.controllers import generate_query
import application

job_stat_api_pages = Blueprint('job_stat_api', __name__
	, template_folder='templates', static_folder='static')

@job_stat_api_pages.route("/<string:metric>/<string:aggregation_function>")
@crossdomain(origin='*')
def get_metric(metric: str, aggregation_function: str) -> Response:

	if aggregation_function not in ["min", "max", "avg", "count", "sum"]:
		raise RuntimeError("bad aggregation function: " + aggregation_function)

	result = generate_query(request.args, metric, aggregation_function)

	return application.helpers.gen_csv_response(result.column_descriptions, result.all())
