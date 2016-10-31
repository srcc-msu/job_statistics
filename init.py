from optparse import OptionParser
import sys

from application.helpers import app_log
from application.setup import create_app, setup_database, load_cluster_config

if __name__ == '__main__':
	parser = OptionParser()

	parser.add_option("--drop", dest="drop", default=False, action="store_true", help="DROP old db and recreate it")
	parser.add_option("-c", "--config", dest="config", default="dev", help="[dev]elopment or [prod]uction configuration")

	(options, args) = parser.parse_args()

	if not options.drop:
		print("SKIP: not dropping unless using --drop key")
		sys.exit(1)

	app = create_app(options.config)
	load_cluster_config("cluster_config/", app)

	app_log("recreating db")
	setup_database(app, options.drop)

	app_log("done")
