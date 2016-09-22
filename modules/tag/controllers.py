from flask import Blueprint, render_template, Response

from core.tag.models import Tag

tag_pages = Blueprint('tag', __name__
	, template_folder='templates', static_folder='static')

@tag_pages.route("/list")
def urls() -> Response:
	tags = Tag.query.all()

	return render_template("tag_list.html", tags=tags)

