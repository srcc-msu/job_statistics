import time

from flask import Blueprint, Response, render_template, request, Flask, current_app

from application.database import global_db
from application.helpers import background
from modules.autotag.models import AutoTag, apply_autotags
from core.job.models import Job
from core.tag.models import Tag
from application.helpers import requires_auth

autotag_pages = Blueprint('autotag', __name__
	, template_folder='templates/', static_folder='static')

@autotag_pages.route("/list")
@requires_auth
def autotag_list() -> Response:
	data = global_db.session.query(Tag, AutoTag).join(AutoTag).order_by(Tag.id).all()
	return render_template("autotag_list.html", data=data)
