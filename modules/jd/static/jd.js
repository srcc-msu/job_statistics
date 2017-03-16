function ConvertForMultiLine(input)
{
    var header = ["min", "max", "avg", "avg_min", "avg_max"];

    var data = [];

    for(var i = 0; i < input.length; i++)
    {
        var tmp = [];

        tmp.push(new Date(input[i]["time"]*1000));

        for(var j = 0; j < header.length; j++)
            tmp.push(parseFloat(input[i][header[j]]));

        data.push(tmp);
    }

    return data;
}

function Shrink(input)
{
	var scale_factor = 500;

	if(input.length < scale_factor)
		return input;

	var new_data = [];

	var factor = Math.floor(input.length / scale_factor);

	for(var i = 0; i < input.length - factor; i += factor)
    {
        var tmp = input[i];

		for(var j = 1; j < factor; j++)
		{
			if(input[i+j][1] < tmp[1]) tmp[1] = input[i+j][1];
			if(input[i+j][2] > tmp[2]) tmp[2] = input[i+j][2];

			tmp[3] += input[i+j][3];
			tmp[4] += input[i+j][4];
			tmp[5] += input[i+j][5];
		}

		tmp[3] /= factor;
		tmp[4] /= factor;
		tmp[5] /= factor;

        new_data.push(tmp);
    }

    return new_data;
}

function LoadOne(name, task_id){
    jQuery.get("/api/job/" + task_id + "/sensor/" + name, function(input) {
        var raw_data = ConvertForMultiLine(input);
		var display_data = Shrink(raw_data);

        var options = {
//            title: name
            legend: { position: 'bottom' }
            , 'chartArea': {backgroundColor: "#f8f8f8", left: 50, top: 20, 'height': '80%', 'width': '100%'}
            , hAxis: { format: 'HH:mm' } // 'dd/MM/yyyy HH:mm'
            , vAxis: { format: 'short', minValue: 0}
            , 'height': 400
            , series: {
                0: { lineWidth: 2 },
                1: { lineWidth: 2 },
                2: { lineWidth: 2 },
                3: { lineWidth: 2 },
                4: { lineWidth: 2 }
            }
            , colors: ['#c0504d', '#4bacc6', '#95b456', '#7b609c', '#f79646']
        };

        var data = new google.visualization.DataTable();
        data.addColumn('datetime', 'time');
        data.addColumn('number', 'min');
        data.addColumn('number', 'max');
        data.addColumn('number', 'avg');
        data.addColumn('number', 'avg_min');
        data.addColumn('number', 'avg_max');
        data.addRows(display_data);

        var chart = new google.visualization.LineChart(document.getElementById(name));

        google.visualization.events.addListener(chart, "select", function() { highlightLine(chart, data, options); });

        chart.draw(data, options);
    });
}

function highlightLine(chart, data, options) {
    var def_lw = 2;
    var unselected_lw = 1;
    var selected_lw = 4;

    var last_selected = -1;
    var selected = chart.getSelection()[0].column - 1;

    for(var i in options.series) {
        if(options.series[i].lineWidth == selected_lw)
            last_selected = i;
    }

    if(selected == last_selected) // unselect
    {
        for(var i in options.series) {
            options.series[i].lineWidth = def_lw;
        }
    }
    else // select
    {
        for(var i in options.series) {
            options.series[i].lineWidth = unselected_lw;
        }
        options.series[selected].lineWidth = selected_lw;
    }

    chart.draw(data, options); //redraw
}

function LoadData(task_id, sensors) {
    for(var i = 0; i < sensors.length; i++)
        LoadOne(sensors[i], task_id);
}

function ApplyToggle(){
    $('.graph').each(function(i) {
        var button = $('<input type="button" value="show/hide" style="float:right;"></input>');
        var graph = this;

        $(graph).before(button);

        var id = graph.id;
        var new_id = id + "_button";

        $(button).attr("id", new_id);

        $("body").on('click', "#" + new_id, function(){
            $(graph).toggle(200);
        });
    });

    ToggleInfo();
}

function ToggleInfo(){
    $('.info').each(function(i) {
        $(this).toggle(200);
    });
}

function ToggleAll(){
    $('.graph').each(function(i) {
        $(this).toggle(200);
    });
}

function FillTags(id)
{
    jQuery.getJSON("/api/job/" + id + "/tags",
        function(data) {
            for(var i = 0; i < data.tags.length; i++)
            {
                $("#jd_tags").append("<li>" + data.tags[i] + "</li>");
            }

            InitTags(id);
        });
}

function InitTags(id)
{
    jQuery.getJSON("/api/tag",
        function(data) {
            var tags = [];

            for(var i = 0; i < data.length; i++)
            {
                tags.push(data[i].label);
            }

            $("#jd_tags").tagit({
                allowSpaces : true,
                availableTags : tags,
                showAutocompleteOnFocus : true,
                placeholderText : "Add tags to this JD",

                beforeTagAdded: function(event, ui) {
                    if(tags.indexOf(ui.tagLabel) == -1)
                    {
                        return false;
                    }
                },

                afterTagAdded: function(event, ui) {
                    if(ui.duringInitialization)
                        return false;
                    $.ajax({
                        type: "POST",
                        url: "/api/job/" + id + "/tag/" + ui.tagLabel,
                        data: { action: "add"},
                    });
                },

                afterTagRemoved: function(event, ui) {
                    $.ajax({
                        type: "POST",
                        url: "/api/job/" + id + "/tag/" + ui.tagLabel,
                        data: { action: "delete"},
                    });
                },

            });
        });
}
