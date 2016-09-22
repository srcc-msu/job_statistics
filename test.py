import unittest

from database import global_db
from core.job.controllers import add
from core.job.models import Job
from core.monitoring.models import JobPerformance
from core.tag.models import JobTag, Tag
from modules.autotag.models import AutoTag
from setup import create_app, setup_database, register_blueprints, load_cluster_config

class TestSuit(unittest.TestCase):
	client = None
	setup = False

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

	@classmethod
	def tearDownClass(cls):
		pass

class GeneralTestSuit(TestSuit):
	def test_menu(self):
		rv = TestSuit.client.get("/menu")
		assert "200" in rv.status
		assert b"All urls" in rv.data

	def test_urls(self):
		rv = TestSuit.client.get("/urls")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"/urls" in rv.data

	def test_preset(self):
		rv = TestSuit.client.get("/job_stat/preset")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"General statistics" in rv.data

	def test_constructor(self):
		rv = TestSuit.client.get("/job_stat/constructor")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"General settings" in rv.data

	def test_table(self):
		rv = TestSuit.client.get("/job_table/table")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"task table" in rv.data

class TestJob(TestSuit):
	test_job = None

	@classmethod
	def setUpClass(cls):
		TestSuit.setUpClass()

		cls.test_job = Job(1, 1, "test", "user", 1, 2, 3, 4, 5, 6, "RUNNING", 1, "command", "./", "node1-001-01")
		add(global_db, cls.test_job)

	def test_short(self):
		rv = TestSuit.client.get("/jd/1")
		print(rv.status, rv.data)

		assert "302" in rv.status

	def test_direct(self):
		rv = TestSuit.client.get("/jd/1/1")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"Job Digest" in rv.data

	def test_account(self):
		rv = TestSuit.client.get("/api/account/user")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"RUNNING" in rv.data

	def test_job_list(self):
		rv = TestSuit.client.get("/api/job/?since=0")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"RUNNING" in rv.data

	def test_create_job_slurm_db(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "slurm_db"
				, "data": "4;test_create_job_slurm_db;test;./;gputest;2;3;4;node1-001-01;1;1;5;6;7"})

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "test_create_job_slurm_db").one()

		assert JobPerformance.query.get(job.id)
		assert JobTag.query.get(job.id)

	def test_create_job_slurm_plugin(self):
		rv = TestSuit.client.post("/api/job/"
			, data={"format" : "slurm_plugin"
				, "data": "JobId=1142390 Name=impi UserId=test_create_job_slurm_plugin(655) GroupId=test_create_job_slurm_plugin(655) Priority=152 Account=test_create_job_slurm_plugin QOS=normal JobState=COMPLETED Reason=None Dependency=(null) Requeue=0 Restarts=0 BatchFlag=1 ExitCode=0:0 DerivedExitCode=0:0 RunTime=00:59:54 TimeLimit=3-00:00:00 TimeMin=N/A SubmitTime=2015-10-30T13:45:57 EligibleTime=2015-10-30T13:45:57 StartTime=2015-10-30T13:45:57 EndTime=2015-11-02T13:45:57 PreemptTime=None SuspendTime=None SecsPreSuspend=0 Partition=regular6 AllocNode:Sid=access2:16866 ReqNodeList=(null) ExcNodeList=(null) NodeList=node4-132-[04-07],node4-134-[07-09],node4-136-[04-07],node4-138-[25-28],node4-142-[22-26],node4-144-[04-07],node4-146-[13-17],node4-148-[04-08],node4-149-[31-32],node4-150-[01-02,04-08] BatchHost=node4-132-04 NumNodes=43 NumCPUs=516 CPUs/Task=1 ReqS:C:T=*:*:*   Nodes=node4-132-[04-07],node4-134-[07-09],node4-136-[04-07],node4-138-[25-28],node4-142-[22-26],node4-144-[04-07],node4-146-[13-17],node4-148-[04-08],node4-149-[31-32],node4-150-[01-02,04-08] CPU_IDs=0-11 Mem=0 MinCPUsNode=1 MinMemoryNode=0 MinTmpDiskNode=0 Features=(null) Gres=(null) Reservation=(null) Shared=0 Contiguous=0 Licenses=(null) Network=(null) Command=/opt/mpi/wrappers/impi ./cdynak WorkDir=/mnt/msu/users/ztsv/bm_l5_r6"})

		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"id" in rv.data

		job = Job.query.filter(Job.account == "test_create_job_slurm_plugin").one()

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
			rv = TestSuit.client.post("/api/tag/test", data={"description": "test"})
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"test" in rv.data

			rv = TestSuit.client.get("/api/tag/")
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"test" in rv.data

		def test_add_job_tag():
			rv = TestSuit.client.post("/api/job/{0}/tag/test".format(TestJobTag.test_job.id), data={"action" : "add"})
			print(rv.status, rv.data)

			assert "200" in rv.status
			assert b"true" in rv.data

		def test_delete_job_tag():
			rv = TestSuit.client.post("/api/job/{0}/tag/test".format(TestJobTag.test_job.id), data={"action" : "delete"})
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
		rv = TestSuit.client.get("/autotag/list")
		print(rv.status, rv.data)

		assert "200" in rv.status
		assert b"t_end" in rv.data

	def test_job_update(self):
		rv = TestSuit.client.post("/autotag/job/1")
		print(rv.status, rv.data)

		assert "202" in rv.status

if __name__ == "__main__":
	unittest.main(verbosity=2)
