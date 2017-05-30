import unittest
import base64

from application.database import global_db
from application.setup import create_app, setup_database, register_blueprints, load_cluster_config
from core.job.controllers import add
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag, Tag
from core.job.helpers import id2hash, hash2id, username2id, id2username
from modules.autotag.models import AutoTag

class TestSuit(unittest.TestCase):
	client = None
	setup = False

	auth_headers = {}

	@classmethod
	def setUpClass(cls):
		TestSuit.app = create_app("testing")
		load_cluster_config("cluster_config/", TestSuit.app)

		if not TestSuit.setup:
			setup_database(TestSuit.app, True)
			print("db created")
			TestSuit.setup = True
		else:
			global_db.init_app(TestSuit.app)
			print("db reused")

		register_blueprints(TestSuit.app)

		TestSuit.client = TestSuit.app.test_client()

		TestSuit.app_context = TestSuit.app.app_context()
		TestSuit.app_context.push()

		login = TestSuit.app.config.get("LOGIN")
		password = TestSuit.app.config.get("PASSWORD")

		TestSuit.auth_headers['Authorization']\
			= 'Basic '.encode() + base64.b64encode("{0}:{1}".format(login, password).encode())

	@classmethod
	def tearDownClass(cls):
		pass

class GeneralTestSuit(TestSuit):
	def test_menu(self):
		rv = TestSuit.client.get("/menu"
			, headers = TestSuit.auth_headers)
		assert "200" in rv.status
		assert b"All urls" in rv.data

	def test_urls(self):
		rv = TestSuit.client.get("/urls"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"/urls" in rv.data

	def test_preset(self):
		rv = TestSuit.client.get("/job_stat/preset"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"General statistics" in rv.data

	def test_constructor(self):
		rv = TestSuit.client.get("/job_stat/constructor"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"General settings" in rv.data

	def test_table(self):
		rv = TestSuit.client.get("/job_table/table/page/0" # bug with redirect and headers?
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"task table" in rv.data

	def test_timeline(self):
		rv = TestSuit.client.get("/job_table/timeline"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"running tasks" in rv.data

	def test_queue_timeline(self):
		rv = TestSuit.client.get("/job_table/queue_timeline"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"queued task" in rv.data

	def test_analyzer_running(self):
		rv = TestSuit.client.get("/analyzer/running"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"running" in rv.data

	def test_api_analyzer_running(self):
		rv = TestSuit.client.get("/api/analyzer/running"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"[" in rv.data

class TestJob(TestSuit):
	test_job = None

	@classmethod
	def setUpClass(cls):
		TestSuit.setUpClass()

		cls.test_job = Job(1, 1, "test", "user", 1, 2, 3, 4, 5, 6, "RUNNING", 1, "command", "./", "node1-001-01")
		add(global_db, cls.test_job)

	def test_short(self):
		rv = TestSuit.client.get("/jd/1"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "302" in rv.status

	def test_direct(self):
		rv = TestSuit.client.get("/jd/1/1"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"Job Digest" in rv.data

	def test_create_job_slurm_db(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "slurm_db"
				, "stage": "BEFORE"
				, "data": "4;test_create_job_slurm_db;test;./;gputest;2;3;4;node1-001-01;1;1;5;6;7"}
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "test_create_job_slurm_db").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)

	def test_create_job_sacct(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "sacct"
				, "stage": "BEFORE"
				, "data" : "5476|compute|serg|2016-01-14T17:21:23|2016-01-14T17:21:23|2016-01-14T17:21:26|1-00:00:00|COMPLETED|4294900803|2|20|n[48021-48022,51000-51010]"}
			, headers=TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "serg").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)

	def test_recreate_job_sacct(self):
		_ = TestSuit.client.post("/api/job/"
			, data={"format" : "sacct"
				, "stage": "BEFORE"
				, "data" : "54761|compute|tttttttt|2016-01-14T17:21:23|2016-01-14T17:21:23|2016-01-14T17:21:26|1-00:00:00|COMPLETED|4294900803|2|20|n[48021-48022,51000-51010]"}
			, headers = TestSuit.auth_headers)

		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "sacct"
				, "stage": "AFTER"
				, "data" : "54761|compute|tttttttt|2016-01-14T17:21:23|2016-01-14T17:21:23|2016-01-14T17:21:26|1-00:00:00|COMPLETED|4294900803|2|20|n[48021-48022,51000-51010]"}
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "tttttttt").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)

	def test_missing_job_sacct(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "sacct"
				, "stage": "ONLY_MISSING"
				, "data" : "54763|compute|tttt|2016-01-14T17:21:23|2016-01-14T17:21:23|2016-01-14T17:21:26|1-00:00:00|COMPLETED|4294900803|2|20|n[48021-48022,51000-51010]"}
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "sacct"
				, "stage": "ONLY_MISSING"
				, "data" : "54763|compute|tttt|2016-01-14T17:21:23|2016-01-14T17:21:23|2016-01-14T17:21:26|1-00:00:00|COMPLETED|4294900803|2|20|n[48021-48022,51000-51010]"}
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"skipping" in rv.data

		job = Job.query.filter(Job.account == "tttt").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)

	def test_create_job_slurm_plugin_2_5_6(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "slurm_plugin"
				, "stage": "BEFORE"
				, "data": "JobId=1142390 Name=impi UserId=test_create_job_slurm_plugin_2(655) GroupId=test_create_job_slurm_plugin(655) Priority=152 Account=test_create_job_slurm_plugin QOS=normal JobState=COMPLETED Reason=None Dependency=(null) Requeue=0 Restarts=0 BatchFlag=1 ExitCode=0:0 DerivedExitCode=0:0 RunTime=00:59:54 TimeLimit=3-00:00:00 TimeMin=N/A SubmitTime=2015-10-30T13:45:57 EligibleTime=2015-10-30T13:45:57 StartTime=2015-10-30T13:45:57 EndTime=2015-11-02T13:45:57 PreemptTime=None SuspendTime=None SecsPreSuspend=0 Partition=regular6 AllocNode:Sid=access2:16866 ReqNodeList=(null) ExcNodeList=(null) NodeList=node4-132-[04-07],node4-134-[07-09],node4-136-[04-07],node4-138-[25-28],node4-142-[22-26],node4-144-[04-07],node4-146-[13-17],node4-148-[04-08],node4-149-[31-32],node4-150-[01-02,04-08] BatchHost=node4-132-04 NumNodes=43 NumCPUs=516 CPUs/Task=1 ReqS:C:T=*:*:*   Nodes=node4-132-[04-07],node4-134-[07-09],node4-136-[04-07],node4-138-[25-28],node4-142-[22-26],node4-144-[04-07],node4-146-[13-17],node4-148-[04-08],node4-149-[31-32],node4-150-[01-02,04-08] CPU_IDs=0-11 Mem=0 MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0 Features=(null) Gres=(null) Reservation=(null) Shared=0 Contiguous=0 Licenses=(null) Network=(null) Command=/opt/mpi/wrappers/impi ./cdynak WorkDir=/mnt/msu/users/ztsv/bm_l5_r6"}
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "test_create_job_slurm_plugin_2").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)

	def test_create_job_slurm_plugin_15_08(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "slurm_plugin"
				, "stage": "BEFORE"
				, "data": "JobId=98865 JobName=3cont.sh UserId=test_create_job_slurm_plugin_15(10035) GroupId=users(10000) Priority=100000000 Nice=0 Account=ivanov QOS=normal JobState=RUNNING Reason=None Dependency=(null) Requeue=0 Restarts=0 BatchFlag=1 Reboot=0 ExitCode=0:0 DerivedExitCode=0:0 RunTime=6-01:17:37 TimeLimit=6-22:40:00 TimeMin=N/A SubmitTime=2016-10-26T15:12:09 EligibleTime=2016-10-26T15:12:09 StartTime=2016-10-26T15:12:12 EndTime=2016-11-02T13:52:12 PreemptTime=None SuspendTime=None SecsPreSuspend=0 Partition=compute AllocNode:Sid=access-02:29092 ReqNodeList=(null) ExcNodeList=(null) NodeList=n50216 BatchHost=n50216 NumNodes=1 NumCPUs=14 CPUs/Task=1 ReqB:S:C:T=0:0:*:* TRES=cpu=14,node=1 Socks/Node=* NtasksPerN:B:S:C=0:0:*:* CoreSpec=*   Nodes=n50216 CPU_IDs=0-13 Mem=0 MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0 Features=(null) Gres=(null) Reservation=(null) Shared=0 Contiguous=0 Licenses=(null) Network=(null) Command=/mnt/scratch/users/ivanov/something/pull_spec_collapsed_2048/3cont.sh WorkDir=/mnt/scratch/users/ivanov/something/pull_spec_collapsed_2048 StdErr=/mnt/scratch/users/ivanov/something/pull_spec_collapsed_2048/slurm-98865.out StdIn=/dev/null StdOut=/mnt/scratch/users/ivanov/something/pull_spec_collapsed_2048/slurm-98865.out Power= SICP=0"}
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "test_create_job_slurm_plugin_15").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)


class TestJd(TestSuit):
	test_job = None

	@classmethod
	def setUpClass(cls):
		TestSuit.setUpClass()

		cls.test_job = Job(2, 2, "test", "account", 1, 2, 3, 4, 5, 6, "RUNNING", 1, "command", "./", "node1-001-01")
		add(global_db, cls.test_job)


	def test_info(self):
		rv = TestSuit.client.get("/api/job/{0}/info".format(TestJd.test_job.id))
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"RUNNING" in rv.data

	def test_perf(self):
		rv = TestSuit.client.get("/api/job/{0}/performance".format(TestJd.test_job.id))
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"cpu_user" in rv.data

	def test_sensor(self):
		rv = TestSuit.client.get("/api/job/{0}/sensor/cpu_user".format(TestJd.test_job.id))
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"[]" in rv.data

	def test_heatmap(self):
		rv = TestSuit.client.get("/jd/{0}/{1}/heatmap/cpu_user".format(TestJd.test_job.job_id, TestJd.test_job.task_id)
			, headers = TestSuit.auth_headers)

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"heatmap" in rv.data

	def test_username_hashing(self):
		for username in ["faf", "fdsfsv", "sags_432", "dvcbsxn4262fz_1234fdsf"]:

			id = username2id(username)
			print(id, username, id2username(id))

			assert id2username(id) == username

	def test_hashing(self):
		for id in [10, 1234, 9432, 25271]:
			hash = id2hash(id)
			print(id, hash, hash2id(hash))

			assert hash2id(hash) == id

class TestJobTag(TestSuit):
	test_job = None

	@classmethod
	def setUpClass(cls):
		TestSuit.setUpClass()

		cls.test_job = Job(3, 3, "test", "account", 1, 2, 3, 4, 5, 6, "RUNNING", 1, "command", "./", "node1-001-01")
		add(global_db, cls.test_job)

	def test_job_tags(self):
		rv = TestSuit.client.get("/api/job/{0}/tags".format(TestJobTag.test_job.id))
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"tags" in rv.data

	def test_job_tag(self):
		rv = TestSuit.client.get("/api/job/{0}/tag/test".format(TestJobTag.test_job.id))
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"false" in rv.data

	def test_tag_complex(self):
		def test_register_tag():
			rv = TestSuit.client.post("/api/tag/test"
				, data={"description": "test"}
				, headers = TestSuit.auth_headers)
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"test" in rv.data

			rv = TestSuit.client.get("/api/tag/")
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"test" in rv.data

		def test_add_job_tag():
			rv = TestSuit.client.post("/api/job/{0}/tag/test".format(TestJobTag.test_job.id)
				, data={"action" : "add"}
				, headers=TestSuit.auth_headers)
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"true" in rv.data

		def test_delete_job_tag():
			rv = TestSuit.client.post("/api/job/{0}/tag/test".format(TestJobTag.test_job.id), data={"action" : "delete"}
				, headers=TestSuit.auth_headers)
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"false" in rv.data

		test_register_tag()
		test_add_job_tag()
		test_delete_job_tag()

class TestJobStat(TestSuit):
	test_job = None

	@classmethod
	def setUpClass(cls):
		TestSuit.setUpClass()

		cls.test_job = Job(4, 4, "test", "account", 1, 2, 3, 4, 5, 6, "RUNNING", 1, "command", "./", "node1-001-01")
		add(global_db, cls.test_job)

	def test_avg(self):
		rv = TestSuit.client.get("/api/job_stat/run_time/avg?t_from=1&t_to=2")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"avg_run_time" in rv.data

class TestAutoTag(TestSuit):
	test_job = None

	@classmethod
	def setUpClass(cls):
		TestSuit.setUpClass()

		cls.test_job = Job(5, 5, "test", "account", 1, 2, 3, 4, 5, 6, "RUNNING", 1, "command", "./", "node1-001-01")
		add(global_db, cls.test_job)

		tag = Tag("test2", "test2")
		global_db.session.add(tag)
		global_db.session.commit()

		autotag = AutoTag(tag.id, "job.t_end > 0")
		global_db.session.add(autotag)
		global_db.session.commit()

	def test_list(self):
		rv = TestSuit.client.get("/autotag/list"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"t_end" in rv.data

	def test_api_list(self):
		rv = TestSuit.client.get("/api/autotag/"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"test2" in rv.data

	def test_create(self):
		rv = TestSuit.client.post("/api/autotag/"
			, data={"label": "test2", "condition": "true"}
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert AutoTag.query.get(eval(rv.data)["id"]) is not None

		assert "200" in rv.status
		assert b"test2" in rv.data

	def test_delete(self):
		rv = TestSuit.client.post("/api/autotag/"
			, data={"label": "test2", "condition": "true"}
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		id = eval(rv.data)["id"]

		rv = TestSuit.client.post("/api/autotag/" + str(id)
			, data={"action": "delete"}, headers = TestSuit.auth_headers)

		assert "200" in rv.status
		assert AutoTag.query.get(id) is None

	def test_job_update(self):
		rv = TestSuit.client.post("/api/autotag/job/1/apply"
			, headers = TestSuit.auth_headers)
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"ok" in rv.data

if __name__ == "__main__":
	unittest.main(verbosity=2)
