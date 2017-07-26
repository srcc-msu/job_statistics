from optparse import OptionParser
from application.database import global_db

from application.helpers import app_log
from application.setup import create_app, setup_database, register_blueprints, load_cluster_config
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag, Tag
from modules.autotag.models import AutoTag

def run(config: str):
	app = create_app(config)
	load_cluster_config("cluster_config/", app)

	app_log("loading db")
	setup_database(app, False)

	app_log("loading blueprints")
	register_blueprints(app)

	return app

if __name__ == '__main__':
	parser = OptionParser()

	parser.add_option("-c", "--config", dest="config", default="dev", help="[dev]elopment or [prod]uction configuration")
	parser.add_option("-t", "--t_end", dest="t_end", default=1483025545, help="include tasks completed after [t_end] timestamp")
	(options, args) = parser.parse_args()

	app = run(options.config)

	@app.before_first_request
	def tagit():
			print("starting tagging")
			conditions = []

			for autotag in AutoTag.query.all():
					conditions.append((autotag.compile_condition(), Tag.query.get(autotag.fk_tag_id).label))

			query = global_db.session \
			.query(Job, JobPerformance, JobTag) \
			.filter(Job.t_end > options.t_end) \
			.join(JobPerformance)\
			.join(JobTag)

			for job,perf,job_tag in query.all():
					tags = ""

					for condition, label in conditions:
							try:
									if condition(job, perf):
											tags += ";{0}".format(label)
							except:
								pass

					print("{0},{1}".format(job.id, tags))

	app.run(host=app.config.get("HOST", "localhost"), port=app.config.get("PORT", 5000) + 10, use_reloader=False)
