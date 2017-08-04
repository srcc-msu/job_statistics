import sys
from cluster_config.node_switch_map import node_switch_map

aggregation_interval = 180

RED = "#ff8080"
YELLOW = "#ffff80"
GREEN = "#80ff80"
WHITE = "#ffffff"

thresholds = {
	"cpu_user": (((0, 20), RED), ((20, 80), YELLOW), ((80, 1e20), GREEN)),

	"gpu_load": (((0, 20), RED), ((20, 80), YELLOW), ((80, 1e20), GREEN)),
	"gpu_mem_load": (((0, 20), RED), ((20, 80), YELLOW), ((80, 1e20), GREEN)),

	"fixed_counter1": (((0, 1e7), RED), ((1e7, 1e8), YELLOW), ((1e8, 1e20), GREEN)),
	"fixed_counter2": (((1e7, 1e20), RED), ((1e5, 1e7), YELLOW), ((0, 1e7), GREEN)),
	"fixed_counter3": (((0, 1e7), RED), ((1e7, 1e8), YELLOW), ((1e8, 1e20), GREEN)),

	"perf_counter1": (((0, 1e7), RED), ((1e7, 1e8), YELLOW), ((1e8, 1e20), GREEN)),
	"perf_counter2": (((1e7, 1e20), RED), ((1e5, 1e7), YELLOW), ((0, 1e7), GREEN)),
	"perf_counter3": (((0, 1e6), RED), ((1e6, 1e8), YELLOW), ((1e8, 1e20), GREEN)),
	"perf_counter4": (((0, 1e6), RED), ((1e6, 1e8), YELLOW), ((1e8, 1e20), GREEN)),

	"ib_rcv_data_fs": (((0, 1e6), RED), ((1e6, 1e7), YELLOW), ((1e7, 1e20), GREEN)),
	"ib_xmit_data_fs": (((0, 1e6), RED), ((1e6, 1e7), YELLOW), ((1e7, 1e20), GREEN)),
	"ib_rcv_pckts_fs": (((0, 1e3), RED), ((1e3, 1e5), YELLOW), ((1e5, 1e20), GREEN)),
	"ib_xmit_pckts_fs": (((0, 1e3), RED), ((1e3, 1e5), YELLOW), ((1e5, 1e20), GREEN)),

	"ib_rcv_data_mpi": (((0, 1e6), RED), ((1e6, 1e7), YELLOW), ((1e7, 1e20), GREEN)),
	"ib_xmit_data_mpi": (((0, 1e6), RED), ((1e6, 1e7), YELLOW), ((1e7, 1e20), GREEN)),
	"ib_rcv_pckts_mpi": (((0, 1e3), RED), ((1e3, 1e5), YELLOW), ((1e5, 1e20), GREEN)),
	"ib_xmit_pckts_mpi": (((0, 1e3), RED), ((1e3, 1e5), YELLOW), ((1e5, 1e20), GREEN)),

	"loadavg": (((0, 2), RED), ((2, 13), YELLOW), ((13, 29), GREEN), ((29, 1e20), RED)),

	"cpu_nice": (((0, 20), GREEN), ((20, 80), YELLOW)),

	"cpu_system": (((80, 1e20), RED), ((20, 80), YELLOW), ((0, 20), GREEN)),
	"cpu_idle": (((80, 1e20), RED), ((20, 80), YELLOW), ((0, 20), GREEN)),
	"cpu_iowait": (((80, 1e20), RED), ((20, 80), YELLOW), ((0, 20), GREEN)),

	"cpu_irq": (((50, 1e20), RED), ((10, 50), YELLOW), ((0, 10), GREEN)),
	"cpu_soft_irq": (((50, 1e20), RED), ((10, 50), YELLOW), ((0, 10), GREEN)),
}

GENERAL_SENSOR_LIST = ["cpu_user", "loadavg", "memory_free"
	, "perf_counter1", "perf_counter2", "fixed_counter2"#, "fixed_counter3"
	, "ib_rcv_data_mpi", "ib_xmit_data_mpi", "ib_rcv_pckts_mpi", "ib_xmit_pckts_mpi"
	, "ib_rcv_data_fs", "ib_xmit_data_fs", "ib_rcv_pckts_fs", "ib_xmit_pckts_fs"
	, "fixed_counter1", "perf_counter3", "perf_counter4"
	, "cpu_nice", "cpu_system", "cpu_idle", "cpu_iowait", "cpu_irq", "cpu_soft_irq"]

GPU_SENSOR_LIST = ["gpu_load", "gpu_mem_load", "gpu_mem_usage"]

SENSOR_LIST = GENERAL_SENSOR_LIST + GPU_SENSOR_LIST

DISPLAY_SENSOR_LIST = ["avg_cpu_user", "avg_loadavg", "avg_ib_rcv_data_mpi", "avg_ib_rcv_data_fs"]

SENSOR_INFO = {
	"cpu_user" : ("CPU user load in %", """CPU user load, minimum 0, max 100
		Percent of time a core was busy with user task (not including io/system work and so on)""")

	, "gpu_load" : ("GPU user load in %", """GPU load in percent, as reported by NVML""")
	, "gpu_mem_load" : ("GPU memory load in %", """GPU memory load in percent, as reported by NVML""")
	, "gpu_mem_usage" : ("GPU memory usage in B", """GPU memory usage in MB""")

	, "fixed_counter1" : ("Instructions retired", """Counts when the last uop of an instruction retires.
		Config(2016.11.10): CPU_PERF_FIXED01:0x00c0""")
	, "fixed_counter2" : ("Last level cache misses", """CPU last level cache miss counter
		Config(2016.11.10): CPU_PERF_FIXED02:0x412e""")
	, "fixed_counter3" : ("Last level cache references", """CPU last level cache reference counter
		Config(2016.11.10): CPU_PERF_FIXED03:0x4f2e""")

	, "perf_counter1" : ("L1 cache misses", """CPU l1 cache miss counter
		Config(2016.11.01): CPU_PERF_COUNTER01:0x0151
		L1D.REPL: Counts the number of lines brought into the L1 data cache.""")
	, "perf_counter2" : ("L2 cache misses", """CPU l2 cache miss counter
		Config(2016.11.01): CPU_PERF_COUNTER02:0x3F24 # L2_RQSTS.MISS""")

	, "perf_counter3" : ("Memory load UOPS", """All retired memory load uops(!), not ops.
		Config(2016.11.01): CPU_PERF_COUNTER03:0x81D0 # MEM_UOPS_RETIRED.ALL_LOADS""")
	, "perf_counter4" : ("Memory store UOPS", """All retired memory store uops(!), not ops.
		Config(2016.11.01): CPU_PERF_COUNTER04:0x82D0 # MEM_UOPS_RETIRED.ALL_STORE""")

	, "ib_rcv_data_fs" : ("FS IB receive data in B", """Infiniband received data in bytes for fs network""")
	, "ib_xmit_data_fs" : ("FS IB send data in B", """Infiniband sent data in bytes for fs network""")
	, "ib_rcv_pckts_fs" : ("FS IB receive packets", """Infiniband received data in packets for fs network""")
	, "ib_xmit_pckts_fs" : ("FS IB send packets", """Infiniband sent data in packets for fs network""")

	, "ib_rcv_data_mpi" : ("MPI IB receive data in B", """Infiniband received data in bytes for mpi network""")
	, "ib_xmit_data_mpi" : ("MPI IB send data in B", """Infiniband sent data in bytes for mpi network""")
	, "ib_rcv_pckts_mpi" : ("MPI IB receive packets", """Infiniband received data in packets for mpi network""")
	, "ib_xmit_pckts_mpi" : ("MPI IB send packets", """Infiniband sent data in packets for mpi network""")

	, "loadavg" : ("LoadAVG", """Average number of processes ready for execution for last minute.
		see /proc/loadavg (http://man7.org/linux/man-pages/man5/proc.5.html)""")

	, "cpu_system" : ("CPU system load in %", """Percent of time a core was busy in kernel space""")
	, "cpu_iowait" : ("CPU iowait load in %", """CPU iowait load, minimum 0, max 100
		Percent of time a core was idle due to waiting for IO operation to complete""")
	, "cpu_idle" : ("CPU idle in %", """CPU idle load, minimum 0, max 100
		Percent of time a core was in idle state""")
	, "cpu_nice" : ("CPU nice load in %", """Percent of time a core was busy with nice(low priority) tasks""")
	, "cpu_irq" : ("CPU irq load in %", """CPU irq load, minimum 0, max 100
		Percent of time a core was busy with hardware interrupts""")
	, "cpu_soft_irq" : ("CPU soft irq load in %", """CPU soft_irq load, minimum 0, max 100
		Percent of time a core was busy with software interrupts""")
	, "memory_free" : ("Free memory", "Free memeory on node")
}

def get_occupied_switches(job):
	nodes = job.expand_nodelist()

	switches = set()

	for node in nodes:
		try:
			switch = node_switch_map[node]
		except:
			switch = "unknown_switch_" + node # using dummy line to show very bad locality
			print("unable to find switch for " + node, file=sys.stderr)

		switches.add(switch)

	return list(switches)

def get_network_locality(job, occupied_switches):
	"""this formula assumes occupied switches count should be equal to num_nodes / 8"""
	return 1.0 * len(occupied_switches) / (job.num_nodes / 8)

def calculate_derivative(job, monitoring: dict):
	derivative = {}

	try:
		derivative["mem_l1_ratio"] = \
			(monitoring["avg"]["perf_counter3"] + monitoring["avg"]["perf_counter4"]) / monitoring["avg"]["perf_counter1"]
	except:
		pass

	try:
		derivative["l1_l3_ratio"] = \
			monitoring["avg"]["perf_counter1"] / monitoring["avg"]["fixed_counter2"]
	except:
		pass

	try:
		derivative["ib_rcv_pckt_size_fs"] = \
			monitoring["avg"]["ib_rcv_data_fs"] / monitoring["avg"]["ib_rcv_pckts_fs"]
	except:
		pass

	try:
		derivative["ib_xmt_pckt_size_fs"] = \
			monitoring["avg"]["ib_xmit_data_fs"] / monitoring["avg"]["ib_xmit_pckts_fs"]
	except:
		pass

	try:
		derivative["ib_rcv_pckt_size_mpi"] = \
			monitoring["avg"]["ib_rcv_data_mpi"] / monitoring["avg"]["ib_rcv_pckts_mpi"]
	except:
		pass

	try:
		derivative["ib_xmt_pckt_size_mpi"] = \
			monitoring["avg"]["ib_xmit_data_mpi"] / monitoring["avg"]["ib_xmit_pckts_mpi"]
	except:
		pass

	try:
		switches = get_occupied_switches(job)
		derivative["network_leaf_switches"] = len(switches)
		derivative["network_locality (1.0=ideal)"] = get_network_locality(job, switches)
	except:
		pass


	return derivative
