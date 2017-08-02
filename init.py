from optparse import OptionParser

from application.setup import create_app, setup_database, load_cluster_config

if __name__ == '__main__':
	parser = OptionParser()

	parser.add_option("--drop", dest="drop", default=False, action="store_true", help="DROP old tables and recreate them")
	parser.add_option("-c", "--config", dest="config", default="dev", help="[dev]elopment or [prod]uction configuration")

	(options, args) = parser.parse_args()

	app = create_app(options.config)
	load_cluster_config("cluster_config/", app)

	if options.drop:
		app.logger.info("dropping and creating tables")
	else:
		app.logger.info("creating missing tables")

	setup_database(app, options.drop)

	app.logger.info("done")
