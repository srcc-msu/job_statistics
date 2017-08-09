import logging
from logging.handlers import RotatingFileHandler
import runpy

from flask import Flask

from application.database import global_db
from application.helpers import ts2datetime, float2

def create_job_stat_view(app, name):
	connection = global_db.get_engine(app).connect()
	connection.execute("""
		CREATE VIEW {0} AS
		SELECT id as fk_job_id,
			TEXTCAT(to_char(to_timestamp(t_submit), 'HH24'), 'h') AS submit_hour,
			to_char(to_timestamp(t_submit), 'dy') AS submit_dow,
			to_char(date_trunc('day', to_timestamp(t_submit)), 'YYYY-MM-DD') AS submit_day,
			to_char(to_timestamp(t_submit), 'Mon') AS submit_month,

			TEXTCAT(to_char(to_timestamp(t_start), 'HH24'), 'h') AS start_hour,
			to_char(to_timestamp(t_start), 'dy') AS start_dow,
			to_char(date_trunc('day', to_timestamp(t_start)), 'YYYY-MM-DD') AS start_day,
			to_char(to_timestamp(t_start), 'Mon') AS start_month,

			TEXTCAT(to_char(to_timestamp(t_end), 'HH24'), 'h') AS end_hour,
			to_char(to_timestamp(t_end), 'dy') AS end_dow,
			to_char(date_trunc('day', to_timestamp(t_end)), 'YYYY-MM-DD') AS end_day,
			to_char(to_timestamp(t_end), 'Mon') AS end_month,

			CASE
				WHEN t_end-t_start >= 0 AND t_end-t_start < 60 THEN '1) >1 minute'
				WHEN t_end-t_start >= 60 AND t_end-t_start < 600 THEN '2) 1-10 minutes'
				WHEN t_end-t_start >= 600 AND t_end-t_start < 3600 THEN '3) 10-60 minutes'
				WHEN t_end-t_start >= 3600 AND t_end-t_start < 3600 * 6 THEN '4) 1-6 hours'
				WHEN t_end-t_start >= 3600 * 6 AND t_end-t_start < 3600 * 24 THEN '5) 6-24 hours'
				WHEN t_end-t_start >= 3600 * 24 AND t_end-t_start < 3600 * 72 THEN '6) 24-72 hours'
				ELSE '7) 72+ hours'
			END duration_group,
			CASE
				WHEN num_cores >= 0 AND num_cores <= 8 THEN '1) [0, 8] cores'
				WHEN num_cores >  8 AND num_cores <= 64 THEN '2) (8, 64] cores'
				WHEN num_cores > 64 AND num_cores <= 128 THEN '3) (64, 128] cores'
				WHEN num_cores > 128 AND num_cores <= 512 THEN '4) (128, 512] cores'
				WHEN num_cores > 512 AND num_cores <= 1024 THEN '5) (512, 1024] cores'
				WHEN num_cores > 1024 AND num_cores <= 4096 THEN '6) (1024, 4096] cores'
				WHEN num_cores > 4096 AND num_cores <= 16384 THEN '7) (4096, 16384] cores'
				ELSE '8) [16384, +inf)'
			END size_group
		FROM job""".format(name))

	connection.close()

def drop_job_stat(app):
	connection = global_db.get_engine(app).connect()

	try:
		connection.execute("""DROP TABLE {}""".format("job_stat"))
	except:
		pass

	try:
		connection.execute("""DROP VIEW {}""".format("job_stat"))
	except:
		pass

	connection.close()

# ensure all sqlalchemy models are initialized
from core.common import *

def setup_database(app: Flask, drop = False):
	global_db.init_app(app)

	if drop:
		with app.app_context():
			drop_job_stat(app)
			global_db.drop_all()
			global_db.create_all()

			drop_job_stat(app)
			create_job_stat_view(app, "job_stat") # recreate it as view
	else:
		with app.app_context():
			global_db.create_all()

def create_app(config: str) -> Flask:
	app = Flask(__name__, static_folder=None)

	handler = RotatingFileHandler('flask.log', maxBytes=10*1000*1000, backupCount=1)
	handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s'
		, datefmt='%Y-%m-%d %H:%M:%S'))

	app.logger.handlers.extend(logging.getLogger('gunicorn.error').handlers)
	app.logger.setLevel(logging.INFO)

	app.logger.addHandler(handler)
	app.template_filter('ts2datetime')(ts2datetime)
	app.template_filter('float2')(float2)

	if config == "dev":
		app.config.from_object('config.DevelopmentConfig')
		app.logger.info("starting with development config")
	elif config == "prod":
		app.config.from_object('config.ProductionConfig')
		app.logger.info("starting with production config")
	elif config == "testing":
		app.config.from_object('config.TestingConfig')
		app.logger.info("starting with testing config")
	else:
		raise RuntimeError("specify configuration - dev, prod or testing")

	return app

def load_cluster_config(path, app):
	class Storage(object):
		pass

	app_config = Storage()

	app_config.general = runpy.run_path(path + "/general.py")
	app_config.monitoring = runpy.run_path(path + "/monitoring.py")
	app_config.cluster = runpy.run_path(path + "/cluster.py")

	app_config.user_map = runpy.run_path(path + "/user_map.py")["user_map"]

	app.app_config = app_config

def register_blueprints(app: Flask):
	with app.app_context():
		import application

		import modules.core_api

		import modules.job_table
		import modules.job_stat
		import modules.jd
		import modules.tag
		import modules.autotag
		import modules.job_analyzer
		import modules.job_import

		app.register_blueprint(application.controllers.core_pages, url_prefix='')

		app.register_blueprint(modules.job_table.controllers.job_table_pages, url_prefix='/job_table')
		app.register_blueprint(modules.job_table.api_controllers.job_table_api_pages, url_prefix='/api/job_table')

		app.register_blueprint(modules.job_stat.controllers.job_stat_pages, url_prefix='/job_stat')
		app.register_blueprint(modules.job_stat.api_controllers.job_stat_api_pages, url_prefix='/api/job_stat')

		app.register_blueprint(modules.jd.controllers.jd_pages, url_prefix='/jd')

		app.register_blueprint(modules.tag.controllers.tag_pages, url_prefix='/tag')
		app.register_blueprint(modules.tag.api_controllers.tag_api_pages, url_prefix='/api/tag')

		app.register_blueprint(modules.autotag.controllers.autotag_pages, url_prefix='/autotag')
		app.register_blueprint(modules.autotag.api_controllers.autotag_api_pages, url_prefix='/api/autotag')

		app.register_blueprint(modules.job_analyzer.controllers.job_analyzer_pages, url_prefix='/analyzer')
		app.register_blueprint(modules.job_analyzer.api_controllers.job_analyzer_api_pages, url_prefix='/api/analyzer')

		app.register_blueprint(modules.core_api.info_controllers.job_info_api_pages, url_prefix='/api/job')
		app.register_blueprint(modules.core_api.tag_controllers.job_tag_api_pages, url_prefix='/api/job')
		app.register_blueprint(modules.core_api.monitoring_controllers.job_monitoring_api_pages, url_prefix='/api/job')

		app.register_blueprint(modules.job_import.controllers.job_import_pages, url_prefix='/api/job')
