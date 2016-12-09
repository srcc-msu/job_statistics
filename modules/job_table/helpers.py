from typing import Optional
from numbers import Number

def get_color(name: str, value: Optional[Number], thresholds) -> Optional[str]:
	name = name.replace("avg_", "").replace("min_", "").replace("max_", "") #TODO: fix?

	if name not in thresholds:
		return None

	if value is None:
		return None

	for (min_limit, max_limit), color in thresholds[name]:
		if min_limit <= value < max_limit:
			return color

	return None

def calculate_job_query_stat(query):
	jobs = list(query.all())

	result = {}

	result["cpu_h"] = sum(((job.t_end-job.t_start) * job.num_cores / 3600 for job,perf,tag in jobs))
	result["count"] = len(jobs)
	result["COMPLETED"] = sum((1 for job,perf,tag in jobs if job.state == "COMPLETED" or job.state == "COMPLETING"))
	result["CANCELLED"] = sum((1 for job,perf,tag in jobs if job.state == "CANCELLED"))
	result["TIMEOUT"] = sum((1 for job,perf,tag in jobs if job.state == "TIMEOUT"))
	result["FAILED"] = sum((1 for job,perf,tag in jobs if job.state == "FAILED"))
	result["NODE_FAIL"] = sum((1 for job,perf,tag in jobs if job.state == "NODE_FAIL"))

	print(result)

	return result