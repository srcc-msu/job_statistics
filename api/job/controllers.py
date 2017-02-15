import traceback
import sys

from flask import Blueprint, jsonify, Response, request, redirect, current_app
from sqlalchemy import func, Float

from application.database import global_db
from core.job.controllers import update_existing, add_new
from core.job.models import Job
from core.job.helpers import LomSlurmConverter, SlurmConverter, SacctConverter
from core.monitoring.controllers import update_performance
from core.monitoring.models import JobPerformance, SENSOR_CLASS_MAP
from application.helpers import crossdomain
from modules.autotag.controllers import apply_autotags
from core.tag.models import JobTag, Tag

job_api_pages = Blueprint('job_api', __name__
	, template_folder='templates')

@job_api_pages.route("/", methods=["POST"])
def add_job() -> Response:
	data = request.form["data"]
	stage = request.form["stage"]

	try:
		if request.form["format"].lower() == "slurm_db":
			parsed_data = LomSlurmConverter().ParseConvert(data)
		elif request.form["format"].lower() == "slurm_plugin":
			parsed_data = SlurmConverter().ParseConvert(data)
		elif request.form["format"].lower() == "sacct":
			parsed_data = SacctConverter().ParseConvert(data)
		else:
			return jsonify({"data": "unsupported format", "result": "error"})

	except Exception as e:
		traceback.print_exc(file=sys.stderr)
		print("ERROR LINE: ", data)
		raise e


	if stage == "BEFORE":
		job = add_new(global_db, parsed_data)
	elif stage == "UPDATE_INFO":
		job = update_existing(global_db, parsed_data)
	elif stage == "AFTER":
		job = update_existing(global_db, parsed_data)
		update_performance(current_app._get_current_object(), global_db, job, True)
		apply_autotags(job)
	elif stage == "ONLY_MISSING":
		try:
			job = add_new(global_db, parsed_data)
		except ValueError:
			return jsonify({"result": "skipping"})
		else:
			update_performance(current_app._get_current_object(), global_db, job, True)
			apply_autotags(job)
	else:
		raise RuntimeError({"result": "unsupported operation stage: " + stage})


	return jsonify({"id" : job.id})

@job_api_pages.route("/<int:record_id>")
@crossdomain(origin='*')
def json_job(record_id: int) -> Response:
	return redirect(request.base_url + "/info")

@job_api_pages.route("/<int:record_id>/info")
@crossdomain(origin='*')
def json_job_info(record_id: int) -> Response:
	data = Job.query.get_or_404(record_id)

	return jsonify(data.to_dict())

# monitoring

@job_api_pages.route("/<int:record_id>/performance", methods=["GET", "POST"])
@crossdomain(origin='*')
def json_job_performance(record_id: int) -> Response:
	if request.method == 'GET':
		_ = Job.query.get_or_404(record_id)
		data = JobPerformance.query.get(record_id)

		return jsonify(data.to_dict())
	elif request.method == 'POST':
		job = Job.query.get_or_404(record_id)

		update_performance(current_app._get_current_object(), global_db, job, request.args.get("force") is not None)
		apply_autotags(job)

		return jsonify("update started")

@job_api_pages.route("/<int:record_id>/sensor/<string:sensor>")
@crossdomain(origin='*')
def job_sensor(sensor: str, record_id: int) -> Response:
	job = Job.query.get(record_id)

	sensor_class = SENSOR_CLASS_MAP[sensor]

	offset = current_app.app_config.general["aggregation_interval"]

	filter_nodelist = list(map(current_app.app_config.cluster["node2int"], job.expand_nodelist()))

	query = global_db.session.query(
		sensor_class.time
			, func.min(sensor_class.min).cast(Float).label("min")
			, func.max(sensor_class.max).cast(Float).label("max")
			, func.avg(sensor_class.min).cast(Float).label("avg_min")
			, func.avg(sensor_class.max).cast(Float).label("avg_max")
			, func.avg(sensor_class.avg).cast(Float).label("avg"))\
		.filter(sensor_class.time > job.t_start + offset)\
		.filter(sensor_class.time < job.t_end - offset)\
		.filter(sensor_class.node_id.in_(filter_nodelist))\
		.group_by(sensor_class.time)\
		.order_by(sensor_class.time)

	result = []

	for entry in query.all():
		result.append({
			"time": entry[0]
			, "min" : entry[1]
			, "max" : entry[2]
			, "avg_min" : entry[3]
			, "avg_max" : entry[4]
			, "avg" : entry[5]
		})

	return jsonify(result)

# tags

@job_api_pages.route("/<int:record_id>/tags")
@crossdomain(origin='*')
def job_tags(record_id: int) -> Response:
	job =  Job.query.get_or_404(record_id)

	job_tag = JobTag.query.get(job.id)

	return jsonify(job_tag.to_dict())

@job_api_pages.route("/<int:record_id>/tag/<string:tag>", methods=["GET", "POST"])
def access_job_tag(record_id: int, tag: str) -> Response:
	"""GET = return tag stat, POST = create or delete and return tag stat"""
	job =  Job.query.get_or_404(record_id)

	if request.method == 'POST':
		if request.form["action"].lower() == "add":
			add_job_tag(job, tag)
		elif request.form["action"].lower() == "delete":
			delete_job_tag(job, tag)
		else:
			raise RuntimeError("unsupported tag operation: " + request.form["action"])

	return jsonify({"tag": tag, "job": record_id, "exist": check_job_tag(job, tag)})

def check_job_tag(job: Job, tag: str) -> bool:
	job_tag = JobTag.query.get(job.id)
	return job_tag.contains(tag)

def delete_job_tag(job: Job, tag: str):
	job_tag = JobTag.query.get(job.id)
	job_tag.delete(tag)

def add_job_tag(job: Job, tag: str) -> Response:
	_ = Tag.query.filter(Tag.label == tag).one() # check it is registered

	job_tag = JobTag.query.get(job.id)
	job_tag.add(tag)

# autotags

@job_api_pages.route("/<int:record_id>/autotag", methods=["POST"])
def __apply_autotags(record_id: int) -> Response:
	job = Job.query.get(record_id)

	apply_autotags(job)

	return job_tags(record_id)
