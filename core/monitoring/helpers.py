from typing import List

from flask import current_app

def nodelist2ids(nodelist: List[str]) -> List[int]:
	return list(map(current_app.app_config.cluster["node2int"], nodelist))
