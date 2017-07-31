name = "cluster"
num_cores = 1000

GENERAL_PARTITIONS = ["regular"]
GPU_PARTITIONS = ["gpu"]

PARTITIONS = GENERAL_PARTITIONS + GPU_PARTITIONS

ACTIVE_JOB_STATES = ["RUNNING", "COMPLETING"]
FINISHED_JOB_STATES = ["COMPLETED", "NODE_FAIL", "TIMEOUT", "FAILED", "CANCELLED"]

JOB_STATES = ACTIVE_JOB_STATES + FINISHED_JOB_STATES


def node2int(node):
	"""custom function to convert nodename to int
	this one removes all chars from names like node1-001-01"""
	return int(''.join(filter(lambda x: x.isdigit(), node)))
