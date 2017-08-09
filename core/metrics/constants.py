import runpy

# it has to be like that because sensor list must be known before application
# is initialized and the config is stored by flask tools
# it is needed to dynamically declare all sensor classes

METRIC_LIST = runpy.run_path("cluster_config/metrics.py")["METRIC_LIST"]
