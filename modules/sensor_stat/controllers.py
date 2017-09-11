from flask import Blueprint, render_template, current_app

from application.helpers import requires_auth

sensor_stat_pages = Blueprint('sensor_stat', __name__
	, template_folder='templates', static_folder='static')

@sensor_stat_pages.route("/averages")
@requires_auth
def constructor():
	return render_template("averages.html", app_config=current_app.app_config)

