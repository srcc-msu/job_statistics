from flask import Blueprint, render_template, current_app, Response
from application.database import global_db

from application.helpers import requires_auth
from core.monitoring.models import SENSOR_CLASS_MAP

sensor_heatmap_pages = Blueprint('sensor_heatmap', __name__
	, template_folder='templates', static_folder='static')

import time

def __heatmap():
	cpu = SENSOR_CLASS_MAP["cpu_user"]
	gpu = SENSOR_CLASS_MAP["gpu_load"]

	interval = current_app.app_config.monitoring["aggregation_interval"]

	time_thr = int(time.time() - interval * 3)

	cpu_data = list(global_db.session.query(cpu.node_id, cpu.avg)
		.filter(cpu.time > time_thr)
		.order_by("time desc").all())

	gpu_data = list(global_db.session.query(gpu.node_id, gpu.avg)
		.filter(gpu.time > time_thr)
		.order_by("time desc").all())

	return render_template("cpu.html", cpu_data = cpu_data, gpu_data = gpu_data)

@sensor_heatmap_pages.route("/general")
@requires_auth
def heatmap() -> Response:
	return __heatmap()
