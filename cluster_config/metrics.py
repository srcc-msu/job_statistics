import sys
from cluster_config.node_switch_map import node_switch_map
from core.job.helpers import expand_nodelist

NODES_PER_SWITCH = 8

def get_occupied_switches(job):
	nodes = expand_nodelist(job["nodelist"])

	switches = set()

	for node in nodes:
		try:
			switch = node_switch_map[node]
		except:
			switch = "unknown_switch_" + node # using dummy line to show very bad locality
			print("unable to find switch for " + node, file=sys.stderr)

		switches.add(switch)

	return list(switches)

def calculate_network_locality(job, occupied_switches):
	return 1.0 * len(occupied_switches) / ((job["num_nodes"] - 1) // NODES_PER_SWITCH + 1)

def _test_package(checklist, res, command, workdir):
	if type(checklist) is not list:
		checklist = [checklist]

	for item in checklist:
		if item in command or item in workdir:
			return res
	return None

def classify(command: str, workdir: str):
	command = command.lower()
	workdir = workdir.lower()

	data = [[["cosmoclm", "cosmo-clm"], "COSMO-CLM"]
		, ["vasp", "VASP"]
		, ["abinit", "Abinit"]
		, [["espresso", "qexpresso"], "Quantum Espresso"]
		, ["magma", "Magma"]
		, [["namd"], "NAMD"]
		, [["mdrun", "gmx_mpi", "gromacs"], "Gromacs"]
		, [["lmp_", "lammps"], "LAMMPS"]
		, [["sol-p", "dimonta"], "SOL-P"]
		, ["nwchem", "NWChem"]
		, ["fmm3d", "FMM3D"]
		, [["pmemd", "sander"], "Amber"]
		, [["rosetta", "minirosetta.mpi.linux", "docking_protocol.mpi.linux"], "Rosetta"]
		, [["da_update_bc", "da_wrfvar", "global_enkf_wrf", "ndown", "real", "metgrid", "wrf", "read_wrfnetcdf"], "WRF"]
		, ["octopus_mpi", "Octopus"]
		, [["gamess", "firefly"], "Firefly"]
		, ["cp2k", "CP2K"]
		, ["athena", "Athena"]
		, [["dlpoly", "dl_poly", "dl_classic"], "DL_POLY"]
		, [["charmrun", "namd2"], "NAMD"]
		, ["g09", "Gaussian"]
		, ["mppcrystal", "Crystal"]
		, [["flowvision", "fvsolver"], "FlowVision"]
		, ["materialsstudio", "MaterialsStudio"]
		, ["openfoam", "OpenFOAM"]
		, ["turbomole", "Turbomole"]
		, ["molpro", "Molpro"]
		, ["wien2k", "Wien2k"]
		, ["ncdyna", "NCDYNA"]
		, ["parMatt", "ParMatt"]
		, ["priroda", "Priroda"]
		, ["cabaret", "CABARET"]

		, ["amplxe", "Intel Vtune"]
		, ["advixe", "Intel Advisor"]
		, ["inspxe", "Intel Inspector"]

		, ["pmu-tools", "pmu-tools"]
	]

	for checklist, package in data:
		result = _test_package(checklist, package, command, workdir)
		if result is not None:
			return result

	return "unknown"

def get_package(job, perf):
	return classify(job["command"], job["workdir"])

def get_mem_l1_ratio(job, perf):
	return (perf["avg"]["perf_counter3"] + perf["avg"]["perf_counter4"]) / perf["avg"]["perf_counter1"]

def get_l1_l3_ratio(job, perf):
	return perf["avg"]["perf_counter1"] / perf["avg"]["fixed_counter2"]

def get_ib_rcv_pckt_size(job, perf):
	return perf["avg"]["ib_rcv_data"] / perf["avg"]["ib_rcv_pckts"]

def get_ib_xmit_pckt_size(job, perf):
	return perf["avg"]["ib_xmit_data"] / perf["avg"]["ib_xmit_pckts"]

def get_network_leaf_switches(job, perf):
	switches = get_occupied_switches(job)
	return len(switches)

def get_network_locality(job, perf):
	switches = get_occupied_switches(job)
	return calculate_network_locality(job, switches)

METRIC_LIST = [
	("mem_l1_ratio", "float", get_mem_l1_ratio, "descr"),
	("l1_l3_ratio", "float", get_l1_l3_ratio, "descr"),
	("ib_rcv_pckt_size", "float", get_ib_rcv_pckt_size, "descr"),
	("ib_xmit_pckt_size", "float", get_ib_xmit_pckt_size, "descr"),
	("network_leaf_switches", "int", get_network_leaf_switches, "descr"),
	("network_locality", "float", get_network_locality, "descr"),
	("package", "str", get_package, "descr")
]
