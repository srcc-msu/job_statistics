from functools import partial

from flask import Blueprint, Response, render_template, request, current_app, redirect
from werkzeug.exceptions import abort

from core.job.models import Job
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP
from core.tag.models import JobTag
from core.job.helpers import id2hash, hash2id
from application.database import global_db
from modules.job_table.helpers import get_color

jd_pages = Blueprint('jd', __name__
	, template_folder='templates', static_folder='static')

@jd_pages.route("/<int:job_id>")
def jd_redirect(job_id: int) -> Response:
	return redirect(request.base_url + "/0")

@jd_pages.route("/<int:job_id>/<int:task_id>")
def jd(job_id: int, task_id: int) -> Response:
	try:
		job = Job.get_by_id(job_id, task_id)
	except LookupError:
		abort(404)

	tag = JobTag.query.get(job.id)
	performance = JobPerformance.query.get(job.id)

	return render_template("jd.html", anon=False, id2hash=id2hash
		, job=job.to_dict(), tags=tag.to_dict(), monitoring=performance.to_dict()
		, derivative=current_app.app_config.monitoring["calculate_derivative"](performance.to_dict())
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))

@jd_pages.route("/<int:job_id>/<int:task_id>/heatmap/<string:sensor>")
def heatmap(job_id: int, task_id: int, sensor: str) -> Response:
	try:
		job = Job.get_by_id(job_id, task_id)
	except LookupError:
		abort(404)

	sensor_class = SENSOR_CLASS_MAP[sensor]

	filter_nodelist = list(map(current_app.app_config.cluster["node2int"], job.expand_nodelist()))

	offset = current_app.app_config.general["aggregation_interval"]

	query = global_db.session.query(sensor_class.time
			, sensor_class.node_id
			, sensor_class.min
			, sensor_class.max
			, sensor_class.avg)\
		.filter(sensor_class.time > job.t_start + offset)\
		.filter(sensor_class.time < job.t_end - offset)\
		.filter(sensor_class.node_id.in_(filter_nodelist))

	data = query.all()

	nodes = sorted(list(set([line[1] for line in data])))

	data_min = "[" +",".join(map(lambda line: "[{},{},{}]".format(line[0], nodes.index(line[1]), line[2]), data)) + "]"
	data_max = "[" +",".join(map(lambda line: "[{},{},{}]".format(line[0], nodes.index(line[1]), line[3]), data)) + "]"
	data_avg = "[" +",".join(map(lambda line: "[{},{},{}]".format(line[0], nodes.index(line[1]), line[4]), data)) + "]"

	return render_template("heatmap.html", job=job.to_dict(), max_value = max(map(lambda x: max(x[2:]), data))
		, data_min = data_min, data_max = data_max, data_avg = data_avg)

@jd_pages.route("/share/<string:hash>")
def anon_jd(hash: str) -> Response:
	task_id = 0
	job_id = hash2id(hash)

	try:
		job = Job.get_by_id(job_id, task_id)
	except LookupError:
		abort(404)

	tag = JobTag.query.get(job.id)
	performance = JobPerformance.query.get(job.id)

	return render_template("jd.html", anon=True
		, job=job.to_dict(), tags=tag.to_dict(), monitoring=performance.to_dict()
		, derivative=current_app.app_config.monitoring["calculate_derivative"](performance.to_dict())
		, app_config=current_app.app_config
		, get_color=partial(get_color, thresholds=current_app.app_config.monitoring["thresholds"]))
