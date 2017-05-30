from flask import Blueprint, current_app, jsonify, render_template, Response

from application.helpers import requires_auth

core_pages = Blueprint('core', __name__
	, template_folder='templates', static_folder='static')

@core_pages.route("/urls")
@requires_auth
def urls() -> Response:
	output = []
	for rule in sorted(current_app.url_map.iter_rules(), key=lambda x: x.rule):
		line = "{:50s} {:50s} {}".format(rule.rule, rule.endpoint, ','.join(rule.methods))
		output.append(line)

	return jsonify(output)

@core_pages.route("/menu")
@requires_auth
def menu() -> Response:
	return render_template("menu.html")
