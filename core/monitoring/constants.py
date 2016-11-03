import runpy

SENSOR_LIST = runpy.run_path("cluster_config/monitoring.py")["SENSOR_LIST"]
