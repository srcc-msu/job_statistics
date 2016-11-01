import datetime
import time
import re
from typing import Tuple

class DBMSConverter(object):
	def ParseConvert(self, data: str) -> dict:
		raise NotImplementedError("convert function not specified")

class SlurmConverter(DBMSConverter):
	# this works for scontrol -o -d show job fom versions 2.5.6 and 15.08
	fields = ["JobId", " Name", " JobName", " UserId", " GroupId", " Priority", " Account", " QOS", " JobState", " Reason"
		, " Dependency", " Requeue", " Restarts", " BatchFlag", " ExitCode", " DerivedExitCode", " RunTime", " TimeLimit"
		, " TimeMin", " SubmitTime", " EligibleTime", " StartTime", " EndTime", " PreemptTime", " SuspendTime"
		, " SecsPreSuspend", " Partition", " AllocNode:Sid", " ReqNodeList", " ExcNodeList", " NodeList", " BatchHost"
		, " NumNodes", " NumCPUs", " CPUs/Task", " ReqS:C:T", " Nodes", " CPU_IDs", " Mem", " MinCPUsNode"
		, " MinMemoryNode", " MinTmpDiskNode", " Features", " Gres", " Reservation", " Shared", " Contiguous"
		, " Licenses", " Network", " Command", " WorkDir", " Nice"]

	@staticmethod
	def FindLastIndex(job_info: str) -> Tuple[int, str]:
		right_index, right_field = None, None

		for field in SlurmConverter.fields:
			index = job_info.rfind(field)

			if right_index is None or index > right_index:
				right_index, right_field = index, field

		return right_index, right_field

	@staticmethod
	def ParseSlurm(job_info: str) -> dict:
		# job_info = "JobId=1142390 Name=impi UserId=ztsv(655) GroupId=ztsv(655) Priority=152 Account=UsersT500 QOS=normal JobState=COMPLETED Reason=None Dependency=(null) Requeue=0 Restarts=0 BatchFlag=1 ExitCode=0:0 DerivedExitCode=0:0 RunTime=00:59:54 TimeLimit=3-00:00:00 TimeMin=N/A SubmitTime=2015-10-30T13:45:57 EligibleTime=2015-10-30T13:45:57 StartTime=2015-10-30T13:45:57 EndTime=2015-11-02T13:45:57 PreemptTime=None SuspendTime=None SecsPreSuspend=0 Partition=regular6 AllocNode:Sid=access2:16866 ReqNodeList=(null) ExcNodeList=(null) NodeList=node4-132-[04-07],node4-134-[07-09],node4-136-[04-07],node4-138-[25-28],node4-142-[22-26],node4-144-[04-07],node4-146-[13-17],node4-148-[04-08],node4-149-[31-32],node4-150-[01-02,04-08] BatchHost=node4-132-04 NumNodes=43 NumCPUs=516 CPUs/Task=1 ReqS:C:T=*:*:*   Nodes=node4-132-[04-07],node4-134-[07-09],node4-136-[04-07],node4-138-[25-28],node4-142-[22-26],node4-144-[04-07],node4-146-[13-17],node4-148-[04-08],node4-149-[31-32],node4-150-[01-02,04-08] CPU_IDs=0-11 Mem=0 MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0 Features=(null) Gres=(null) Reservation=(null) Shared=0 Contiguous=0 Licenses=(null) Network=(null) Command=/opt/mpi/wrappers/impi ./cdynak WorkDir=/mnt/msu/users/ztsv/bm_l5_r6"
		result = {}

		while True:
			index, field = SlurmConverter.FindLastIndex(job_info)

			if index == -1:
				break

			result[field.strip()] = job_info[index + len(field) + 1:].strip()
			job_info = job_info[:index]

		return result

	@staticmethod
	def SlurmTime2TS(slurm_time: str) -> int:
		parsed = datetime.datetime.strptime(slurm_time, "%Y-%m-%dT%H:%M:%S")

		return int(time.mktime(parsed.timetuple()))

	@staticmethod
	def SlurmInterval2TS(slurm_interval: str) -> int:
		# 01-12:21:12
		result = 0

		check_day = slurm_interval.split("-") # extract day

		if len(check_day) == 2:
			result += int(check_day[0]) * 86400
			slurm_interval = check_day[1]

		hms = slurm_interval.split(":") # extract hms

		result += int(hms[0]) * 3600
		result += int(hms[1]) * 60
		result += int(hms[2])

		return result

	def ParseConvert(self, job_info: str) -> dict:
		raw = self.ParseSlurm(job_info)

		result = {
			"job_id": int(raw["JobId"])
			, "task_id": 0
			, "partition": LomSlurmConverter.CleanPartition(raw["Partition"], raw["NodeList"]) # TODO: :(
			, "account": raw["UserId"].split("(")[0]
			, "t_submit": self.SlurmTime2TS(raw["SubmitTime"])
			, "t_start": self.SlurmTime2TS(raw["StartTime"])
			, "t_end": self.SlurmTime2TS(raw["EndTime"])
			, "timelimit": self.SlurmInterval2TS(raw["TimeLimit"])
			, "command": raw["Command"]
			, "workdir": raw["WorkDir"]
			, "state": raw["JobState"]
			, "priority": int(raw["Priority"])
			, "num_nodes": int(raw["NumNodes"])
			, "num_cores": int(raw["NumCPUs"])
			, "nodelist": raw["NodeList"]}

		return result

class SacctConverter(DBMSConverter):
	def ParseConvert(self, job_info: str) -> dict:
		# sacct -S 2015-01-01 --format=JobID,Partition,User,Submit,Start,End,Timelimit,State,Priority,NNodes,alloccpus,NodeList -P
		# 5476|compute|serg|2016-01-14T17:21:23|2016-01-14T17:21:23|2016-01-14T17:21:26|1-00:00:00|COMPLETED|4294900803|2|20|n[48021-48022]

		raw = job_info.split("|")

		result = {
			"job_id": int(raw[0])
			, "task_id": 0
			, "partition": raw[1]
			, "account": raw[2]
			, "t_submit": SlurmConverter.SlurmTime2TS(raw[3])
			, "t_start": SlurmConverter.SlurmTime2TS(raw[4])
			, "t_end": SlurmConverter.SlurmTime2TS(raw[5])
			, "timelimit": SlurmConverter.SlurmInterval2TS(raw[6])
			, "command": ""
			, "workdir": ""
			, "state": raw[7]
			, "priority": int(raw[8])
			, "num_nodes": int(raw[9])
			, "num_cores": int(raw[10])
			, "nodelist": raw[11]}

		return result

class CleoConverter(DBMSConverter):
	def ParseConvert(self, job_info: str) -> dict:
		# job_info = "9981;shvets;/bin/sleep 100;/export/home/shvets/graphit_jd;main;1452530336;1452530336;1452530441;cn11:1;1;864000;0"

		raw = job_info.split(";")

		nodelist = list(set(re.sub(r":.", "", raw[8]).split(",")))

		result = {
			"job_id": int(raw[0])
			, "task_id": 0
			, "account": raw[1]
			, "command": raw[2]
			, "workdir": raw[3]
			, "partition": raw[4]
			, "t_submit": int(raw[5])
			, "t_start": int(raw[6])
			, "t_end": int(raw[7])
			, "nodelist": ",".join(nodelist)
			, "timelimit": int(raw[10])
			, "state": raw[11]
			, "priority": 0
			, "num_nodes": len(nodelist)
			, "num_cores": int(raw[9])}

		return result

class LomSlurmConverter(DBMSConverter):
	state_map = {
		"0": "PENDING"
		, "1": "RUNNING"
		, "2": "SUSPENDED"
		, "3": "COMPLETED"
		, "4": "CANCELLED"
		, "5": "FAILED"
		, "6": "TIMEOUT"
		, "7": "NODE_FAIL"
		, "8": "PREEMPTED"
		, "9": "END"}

	@staticmethod
	def CleanPartition(partition: str, nodelist: str) -> str:
		if "," in partition:
			if "node1-128" in nodelist:
				return "test"
			elif "node1-130" in nodelist:
				return "test"
			elif "node6-155" in nodelist:
				return "gputest"
			elif "node1" in nodelist:
				return "regular4"
			elif "node4" in nodelist:
				return "regular6"
			elif "node2" in nodelist:
				return "hdd4"
			elif "node5" in nodelist:
				return "hdd6"
			elif "node6" in nodelist:
				return "gpu"
			else:
				return "unknown"
		else:
			return partition

	def ParseConvert(self, job_info: str) -> dict:
		# job_info = "id;account;command;workdir;partition;t_submit;t_start;t_end;nodelist;num_nodes;num_cores;timelimit;state;priority"

		raw = job_info.split(";")

#		if raw[12] in ["0", "1", "2", "8", "9"]: # TODO: ?
#			print("not adding: bad status", job_info)
#			return {}

		result = {
			"job_id": int(raw[0])
			, "task_id": 0
			, "account": raw[1]
			, "command": raw[2]
			, "workdir": raw[3]
			, "partition": LomSlurmConverter.CleanPartition(raw[4], raw[8])
			, "t_submit": int(raw[5])
			, "t_start": int(raw[6])
			, "t_end": int(raw[7])
			, "nodelist": raw[8]
			, "num_nodes": int(raw[9])
			, "num_cores": int(raw[10])
			, "timelimit": int(raw[11])
			, "state": LomSlurmConverter.state_map.get(raw[12], "ERROR_BAD_STATE")
			, "priority": int(raw[13])}

		return result
