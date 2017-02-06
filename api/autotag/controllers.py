from flask import Blueprint, jsonify, Response, request
from helpers import crossdomain

from modules.autotag.models import AutoTag
from application.database import global_db
from core.tag.models import Tag

autotag_api_pages = Blueprint('autotag_api', __name__
	, template_folder='templates', static_folder='static')

@autotag_api_pages.route("/")
@crossdomain(origin='*')
def show_all_tags() -> Response:
	data = global_db.session.query(Tag, AutoTag).join(AutoTag).all()

	return jsonify([{"label": tag.label, "condition": autotag.condition} for tag, autotag in data])

@autotag_api_pages.route("/", methods=["POST"])
def create_tag() -> Response:
	label = request.form["label"]
	condition = request.form["condition"]

	tag = Tag.query.filter(Tag.label == label).one() # check it is registered
	autotag = AutoTag(tag.id, condition)

	global_db.session.add(autotag)
	global_db.session.commit()

	return jsonify({"id": autotag.id, "label": label, "condition": condition})

@autotag_api_pages.route("/<int:autotag_id>", methods=["POST"])
def manage_tag(autotag_id: int) -> Response:
	if request.form["action"].lower() == "delete":

		autotag = AutoTag.query.get(autotag_id)

		global_db.session.delete(autotag)
		global_db.session.commit()

		return "ok"
	else:
		raise RuntimeError("unsupported autotag operation: " + request.form["action"])

