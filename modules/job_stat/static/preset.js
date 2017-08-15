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

function LoadTagStat(tag, target, t_from, t_to, show_users)
{
	var data = {
		t_from: t_from,
		t_to: t_to
	};

	function transform(data)
	{
		var user_count = data.length;
		var tag_count = 0;

		for(var i = 0; i < data.length; i++)
		{
			tag_count += data[i][1];
		}

		if(show_users)
			return tag_count + " (" + user_count + "u)";

		return tag_count;
	}

	AjaxTextWrapper("/api/job_stat/tag/" + tag, data, target, transform);
}

function DrawAvgWaitTime(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "partition,start_day"
		, tasks: "t_start"
	};

	AjaxDrawWrapper("/api/job_stat/metric/wait_time/avg", data, target, true);
}

function DrawUsersCount(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "partition,start_day"
		, tasks: "t_start"
	};

	AjaxDrawWrapper("/api/job_stat/metric/accounts/count", data, target, true);
}

function DrawTopCpuh(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "account"
	};

	AjaxDrawWrapper("/api/job_stat/metric/cores_sec/sum", data, target);
}

function DrawTopCount(target, t_start, t_end)
{
	var data = {
		t_from: t_start
		, t_to: t_end
		, grouping: "account"
	};

	AjaxDrawWrapper("/api/job_stat/metric/jobs/count", data, target);
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

	AjaxTextWrapper("/api/job_stat/metric/cores_sec/sum", data, target, transform);
}

function ShowUserCount(target, t_from, t_to)
{
	var data = {
		t_from: t_from
		, t_to: t_to
	};

	function transform(data) { return parseInt(data.split('\n')[1]); }

	AjaxTextWrapper("/api/job_stat/metric/accounts/count", data, target, transform);
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

	AjaxTextWrapper("/api/job_stat/metric/wait_time/avg", data, target, transform);
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

	AjaxTextWrapper("/api/job_stat/metric/run_time/avg", data, target, transform);
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

	AjaxTextWrapper("/api/job_stat/metric/jobs/count", data, "#avg_" + target, avg_transform);
	AjaxTextWrapper("/api/job_stat/metric/jobs/count", data, "#total_" + target, total_transform);
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

	AjaxTextWrapper("/api/job_stat/metric/jobs/count", data, "#avg_" + target, avg_transform);
	AjaxTextWrapper("/api/job_stat/metric/jobs/count", data, "#total_" + target, total_transform);
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

	AjaxTextWrapper("/api/job_stat/metric/wait_time/avg", data, target, transform);

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

	AjaxTextWrapper("/api/job_stat/metric/avg_cpu_user/avg", data, target, transform);
}
