from flask import Blueprint, Response, request, jsonify
from sqlalchemy import func

from application.database import global_db
from application.helpers import crossdomain, gen_csv_response
from core.monitoring.models import SENSOR_CLASS_MAP

sensor_stat_api_pages = Blueprint('sensor_stat_api', __name__
	, template_folder='templates', static_folder='static')

@sensor_stat_api_pages.route("/avg/<string:sensor>")
@crossdomain(origin='*')
def get_sensor_stat(sensor: str) -> Response:

	try:
		t_from = request.args["t_from"]
		t_to = request.args["t_to"]

		sensor_class = SENSOR_CLASS_MAP[sensor]
	except KeyError as e:
		raise e

	query = (global_db.session.query(
			sensor_class.time
			, func.count(sensor_class.time).label("working_nodes")
			, func.avg(sensor_class.avg).label("avg"))
		.filter(sensor_class.time > t_from)
		.filter(sensor_class.time < t_to)
		.group_by(sensor_class.time)
		.order_by(sensor_class.time))

	return gen_csv_response(query.column_descriptions, query.all())
