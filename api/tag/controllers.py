from flask import Blueprint, jsonify, Response, request

from core.tag.models import Tag
from application.database import global_db
from helpers import crossdomain

tag_api_pages = Blueprint('tag_api', __name__
	, template_folder='templates', static_folder='static')

@tag_api_pages.route("/")
@crossdomain(origin='*')
def show_all_tags() -> Response:
	tags = Tag.query.all()

	return jsonify([{"id": tag.id, "label": tag.label, "description": tag.description} for tag in tags])

@tag_api_pages.route("/<string:label>", methods=["POST"])
def create_tag(label: str) -> Response:
	tag = Tag(label, request.form["description"])

	global_db.session.add(tag)
	global_db.session.commit()

	return jsonify({"tag" : label, "description": request.form["description"]})
