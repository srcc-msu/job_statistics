from flask import Blueprint, render_template, current_app, Response
from application.database import global_db

from application.helpers import requires_auth
from core.monitoring.models import SENSOR_CLASS_MAP

sensor_heatmap_pages = Blueprint('sensor_heatmap', __name__
	, template_folder='templates', static_folder='static')

import time

def __heatmap():
	sensor_class = SENSOR_CLASS_MAP["cpu_user"]

	interval = current_app.app_config.monitoring["aggregation_interval"]

	time_thr = int(time.time() - interval * 2)

	query = (global_db.session.query(sensor_class.node_id, sensor_class.avg)
		.filter(sensor_class.time > time_thr)
		.order_by("time desc")
		.limit(1364))

	data = query.all()

	return render_template("cpu.html", data = data)

@sensor_heatmap_pages.route("/cpu")
@requires_auth
def heatmap() -> Response:
	return __heatmap()
