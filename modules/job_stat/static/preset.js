function DrawCharts(num_cores, timezone_offset)
{
	var midnight = (Date.now() - (Date.now()) % (86400 * 1000)) / 1000 + timezone_offset;
	var last_day = midnight - 60 * 60 * 24 * 1;
	var last_week = midnight - 60 * 60 * 24 * 7;
	var last_month = midnight - 60 * 60 * 24 * 30;
	var since_jan1 = (new Date(new Date().getFullYear(), 0, 1)) / 1000;

	DrawAvgWaitTime("#queue_avg_wait_time_by_day", last_week, midnight);

	DrawTopCpuh("#user_total_work_time", last_week, midnight);
	DrawTopCount("#user_total_tasks", last_week, midnight);

	DrawUsersCount("#users_by_day", last_week, midnight);

	ShowUsage("#task_total_cpu_1", last_day, midnight, num_cores);
	ShowUsage("#task_total_cpu_7", last_week, midnight, num_cores);
	ShowUsage("#task_total_cpu_30", last_month, midnight, num_cores);
	ShowUsage("#task_total_cpu_365", since_jan1, midnight, num_cores);

	ShowCompleted("completed_1", last_day, midnight);
	ShowCompleted("completed_7", last_week, midnight);
	ShowCompleted("completed_30", last_month, midnight);
	ShowCompleted("completed_365", since_jan1, midnight);

	ShowStarted("started_1", last_day, midnight);
	ShowStarted("started_7", last_week, midnight);
	ShowStarted("started_30", last_month, midnight);
	ShowStarted("started_365", since_jan1, midnight);

	ShowRunning("#avg_running_1", last_day, midnight);
	ShowRunning("#avg_running_7", last_week, midnight);
	ShowRunning("#avg_running_30", last_month, midnight);
	ShowRunning("#avg_running_365", since_jan1, midnight);

	ShowWaiting("#avg_waiting_1", last_day, midnight);
	ShowWaiting("#avg_waiting_7", last_week, midnight);
	ShowWaiting("#avg_waiting_30", last_month, midnight);
	ShowWaiting("#avg_waiting_365", since_jan1, midnight);

	ShowUserCount("#total_user_count_1", last_day, midnight);
	ShowUserCount("#total_user_count_7", last_week, midnight);
	ShowUserCount("#total_user_count_30", last_month, midnight);
	ShowUserCount("#total_user_count_365", since_jan1, midnight);

	ShowAvgCPU("#task_stat_avg_cpu_user_1", last_day, midnight);
	ShowAvgCPU("#task_stat_avg_cpu_user_7", last_week, midnight);
	ShowAvgCPU("#task_stat_avg_cpu_user_30", last_month, midnight);
	ShowAvgCPU("#task_stat_avg_cpu_user_365", since_jan1, midnight);

	ShowAvgWaitTime("#task_avg_waittime_1", last_day, midnight);
	ShowAvgWaitTime("#task_avg_waittime_7", last_week, midnight);
	ShowAvgWaitTime("#task_avg_waittime_30", last_month, midnight);
	ShowAvgWaitTime("#task_avg_waittime_365", since_jan1, midnight);

	var tags = ["cls_communicative_volume","cls_communicative_packets","cls_sc_appropriate","cls_not_communicative","cls_serial","cls_suspicious","cls_data_intensive","cls_gpu_pure","cls_gpu_hybrid_good"];

	for(var i = 0; i < tags.length; i++)
	{
		LoadTagStat(tags[i], "#"+tags[i] + "_1", last_day, midnight);
		LoadTagStat(tags[i], "#"+tags[i] + "_7", last_week, midnight);
		LoadTagStat(tags[i], "#"+tags[i] + "_30", last_month, midnight);
		LoadTagStat(tags[i], "#"+tags[i] + "_365", since_jan1, midnight);
	}

}

function AjaxDrawWrapper(api, data, target, sorted)
{
	$.ajax({
		url: api
		, data: data
		, success: function(data) {
			Draw(target, data, 10, false, sorted);}
		, error: function() {
			$(target).val("Internal error"); }
	});
}

function LoadTagStat(tag, target, t_from, t_to)
{
	var data = {
		date_from: t_from
		, date_to: t_to
		, req_tags: tag
		, accounts: ""
		, states: ""
		, partitions: ""
	};

	function transform(data)
	{
		return data.length;
	}

	AjaxTextWrapper("/api/job_table/common", data, target, transform);
}

function DrawAvgWaitTime(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "partition,start_day"
		, tasks: "t_start"
	};

	AjaxDrawWrapper("/api/job_stat/wait_time/avg", data, target, true);
}

function DrawUsersCount(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "partition,start_day"
		, tasks: "t_start"
	};

	AjaxDrawWrapper("/api/job_stat/accounts/count", data, target, true);
}

function DrawTopCpuh(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "account"
	};

	AjaxDrawWrapper("/api/job_stat/cores_sec/sum", data, target);
}

function DrawTopCount(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "account"
	};

	AjaxDrawWrapper("/api/job_stat/jobs/count", data, target);
}

function AjaxTextWrapper(api, data, target, transform_function)
{
	$.ajax({
		url: api
		, data: data
		, success: function(data) {
			$(target).html(transform_function(data).toString()); }
		, error: function() {
			$(target).val("Internal error"); }
	});
}

function ShowUsage(target, t_from, t_to, num_cores)
{
	var data = {
		t_from: t_from
		, t_to: t_to
		, tasks: "t_end"
	};

	function transform(data)
	{
		var cores_sec = (parseInt(data.split('\n')[1])) / (t_to - t_from) / num_cores;

		return (cores_sec * 100).toFixed(1) + "%";
	}

	AjaxTextWrapper("/api/job_stat/cores_sec/sum", data, target, transform);
}

function ShowUserCount(target, t_from, t_to)
{
	var data = {
		t_from: t_from
		, t_to: t_to
	};

	function transform(data) { return parseInt(data.split('\n')[1]); }

	AjaxTextWrapper("/api/job_stat/accounts/count", data, target, transform);
}

function ShowWaiting(target, t_from, t_to)
{
	var data = {
		t_from: t_from
		, t_to: t_to
	};

	function transform(data)
	{
		return (-1).toFixed(1);
	}

	AjaxTextWrapper("/api/job_stat/wait_time/avg", data, target, transform);
}

function ShowRunning(target, t_from, t_to)
{
	var data = {
		t_from: t_from
		, t_to: t_to
	};

	function transform(data)
	{
		return (-1).toFixed(1);
	}

	AjaxTextWrapper("/api/job_stat/run_time/avg", data, target, transform);
}

function ShowCompleted(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, include: "completed"
	};

	function avg_transform(data) { return (parseInt(data.split('\n')[1]) / ((t_end - t_start) / 86400)).toFixed(1); }
	function total_transform(data) { return parseInt(data.split('\n')[1]); }

	AjaxTextWrapper("/api/job_stat/jobs/count", data, "#avg_" + target, avg_transform);
	AjaxTextWrapper("/api/job_stat/jobs/count", data, "#total_" + target, total_transform);
}

function ShowStarted(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, include: "started"
	};

	function avg_transform(data) { return (parseInt(data.split('\n')[1]) / ((t_end - t_start) / 86400)).toFixed(1); }
	function total_transform(data) { return parseInt(data.split('\n')[1]); }

	AjaxTextWrapper("/api/job_stat/jobs/count", data, "#avg_" + target, avg_transform);
	AjaxTextWrapper("/api/job_stat/jobs/count", data, "#total_" + target, total_transform);
}

function ShowAvgWaitTime(target, t_from, t_to)
{
	var data = {
		t_from: t_from
		, t_to: t_to
	};

	function transform(data)
	{
		return (parseInt(data.split('\n')[1]) / 3600).toFixed(1);
	}

	AjaxTextWrapper("/api/job_stat/wait_time/avg", data, target, transform);

}

function ShowAvgCPU(target, t_from, t_to)
{
	var data = {
		t_from: t_from
		, t_to: t_to
	};

	function transform(data)
	{
		return (parseInt(data.split('\n')[1])).toFixed(1);
	}

	AjaxTextWrapper("/api/job_stat/avg_cpu_user/avg", data, target, transform);
}
