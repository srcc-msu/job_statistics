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

def extract_string_list(request: dict, field_name: str):
	result = request.get(field_name, "")

	if len(result) == 0:
		return []

	return result.split(",")

def extract_number(request: dict, field_name: str, default = None):
	result = request.get(field_name)

	try:
		return int(result)
	except (ValueError, TypeError):
		return default