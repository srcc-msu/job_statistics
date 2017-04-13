from optparse import OptionParser

from application.helpers import app_log
from application.setup import create_app, setup_database, register_blueprints, load_cluster_config

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
	(options, args) = parser.parse_args()

	app = run(options.config)

	app_log("running")
	app.run(host=app.config.get("HOST", "localhost"), port=app.config.get("PORT", 5000), use_reloader=False)
