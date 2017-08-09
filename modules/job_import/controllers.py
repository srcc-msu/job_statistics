from flask import Blueprint, jsonify, Response, request, current_app, Flask

from application.database import global_db
from core.common.controllers import update_existing, add_new
from core.job.models import Job
from core.metrics.models import calculate_metrics
from core.monitoring.models import JobPerformance
from application.helpers import background
from modules.autotag.controllers import apply_autotags
from application.helpers import requires_auth
from modules.job_import.helpers import LomSlurmConverter, SlurmConverter, SacctConverter

job_import_pages = Blueprint('job_api', __name__
	, template_folder='templates')

def __update_performance(app: Flask, job: Job, job_performance: JobPerformance):
	with app.app_context():
		job_performance.update(app.app_config.monitoring["aggregation_interval"])
		apply_autotags(job)
		calculate_metrics(job)

def update_performance(job: Job):
	job_performance = JobPerformance.query.get(job.id)
	background(__update_performance, (job, job_performance))

@job_import_pages.route("/<int:record_id>/performance", methods=["POST"])
@requires_auth
def update_job_performance(record_id: int) -> Response:
	job = Job.query.get_or_404(record_id)

	update_performance(job)

	return jsonify("update started")

def __add_job(app: Flask, data: str, stage: str, job_format: str):
	with app.app_context():
		try:
			if job_format == "slurm_db":
				parsed_data = LomSlurmConverter().ParseConvert(data)
			elif job_format == "slurm_plugin":
				parsed_data = SlurmConverter().ParseConvert(data)
			elif job_format == "sacct":
				parsed_data = SacctConverter().ParseConvert(data)
			else:
				raise ValueError("unsupported format: " + data)

		except Exception as e:
			current_app.logger.exception("failed import attempt: " + data)
			raise e

		if stage == "BEFORE":
			job = add_new(global_db, parsed_data)
		elif stage == "UPDATE_INFO":
			job = update_existing(global_db, parsed_data)
		elif stage == "AFTER":
			job = update_existing(global_db, parsed_data)
			update_performance(job)
		elif stage == "ONLY_MISSING":
			try:
				job = add_new(global_db, parsed_data)
			except ValueError:
				pass
			else:
				update_performance(job)
		else:
			raise ValueError("unsupported operation stage: " + stage)

@job_import_pages.route("/", methods=["POST"])
@requires_auth
def add_job() -> Response:
	data = request.form["data"]
	stage = request.form["stage"]
	format = request.form["format"].lower()

	background(__add_job, (data, stage, format))

	return jsonify({"result": "queued"})
