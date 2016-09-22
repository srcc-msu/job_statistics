from typing import Optional
from numbers import Number

def get_color(name: str, value: Optional[Number], thresholds) -> Optional[str]:
	if name not in thresholds:
		return None

	if value is None:
		return None

	for (min_limit, max_limit), color in thresholds[name]:
		if min_limit <= value < max_limit:
			return color

	return None
