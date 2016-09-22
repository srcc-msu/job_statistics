from flask import Blueprint, Response, jsonify

from core.job.models import Job

account_api_pages = Blueprint('account_api', __name__
	, template_folder='templates')

@account_api_pages.route("/<string:account>")
def json_jobs_by_account(account: str) -> Response:
	data = Job.query.filter(Job.account==account).all()

	return jsonify(list(map(lambda x: x.to_dict(), data)))
