function TransferColumn(data, from, to)
{
    for(var i = 0; i < data.length; i++)
    {
        var tmp = data[i][from];
        data[i][from] = data[i][to];
        data[i][to] = tmp;
    }
}

function ReorderArray1d(data, main_key)
{
    TransferColumn(data, data[0].indexOf(main_key), 0);

    return data;
}

function ReorderArray2d(data, main_key, secondary_key)
{
    TransferColumn(data, data[0].indexOf(main_key), 0);
    TransferColumn(data, data[0].indexOf(secondary_key), 1);

    var new_header = [main_key];

    for(var i = 1; i < data.length; i++)
    {
        if(new_header.indexOf(data[i][1]) === -1)
            new_header.push(data[i][1]);
    }

    var main_key_data = [];

    for(var i = 1; i < data.length; i++)
    {
        if(main_key_data.indexOf(data[i][0]) === -1)
            main_key_data.push(data[i][0]);
    }

    var new_data = [];

    new_data[0] = new_header;

    for(var i = 0; i < main_key_data.length; i++)
    {
        var new_line = Array.apply(null, Array(new_header.length)).map(Number.prototype.valueOf, 0);
        new_line[0] = main_key_data[i];
        new_data.push(new_line);
    }

    for(var i = 1; i < data.length; i++)
    {
        new_data[main_key_data.indexOf(data[i][0]) + 1][new_header.indexOf(data[i][1])] = data[i][2];
    }

    return new_data;
}

function ReorderArray(data, main_key, secondary_key)
{
    var secondary_key_index = data[0].indexOf(secondary_key);

    if(secondary_key_index === -1)
        return ReorderArray1d(data, main_key);
    else
        return ReorderArray2d(data, main_key, secondary_key);
}

function ConvertCsvToGoogleCharts(target, csv_data)
{
	var grouping_order = [
        "account"
        , "cluster"
        , "submit_hour"
		, "submit_dow"
		, "submit_day"
		, "submit_month"
		, "start_hour"
		, "start_dow"
		, "start_day"
		, "start_month"
		, "end_hour"
		, "end_dow"
		, "end_day"
		, "end_month"
        , "partition"
        , "state"
        , "size_group"
        , "duration_group"
    ];

    var header = csv_data[0];

	var grouping_count = 0;

    for(var i = 0; i < header.length; i++)
        if($.inArray(header[i], grouping_order) != -1)
            grouping_count++;

    if(grouping_count === 0 || grouping_count > 2 )
    {
        return null;
    }

    var first_grouping, second_grouping;

    for(first_grouping = 0; first_grouping < grouping_order.length; first_grouping++)
    {
        if(header.indexOf(grouping_order[first_grouping]) != -1)
            break;
    }

    for(second_grouping = first_grouping + 1; second_grouping < grouping_order.length; second_grouping++)
    {
        if(header.indexOf(grouping_order[second_grouping]) != -1)
            break;
    }

    return ReorderArray(csv_data, grouping_order[first_grouping], grouping_order[second_grouping]);
}

function SortCsv(csv)
{
    var header = csv[0];

    var data = csv.slice(1);

    data.sort(function(a, b){
        return a[0].localeCompare(b[0]);
    });

    return [header].concat(data);
}

function Draw(target, data, rows_count, normalized, sorted)
{
    var csv_data = $.csv.toArrays(data, { onParseValue: $.csv.hooks.castToScalar});

    var converted_csv = ConvertCsvToGoogleCharts(target, csv_data);

    if(converted_csv === null)
    {
        $(target).val("draw error - bad params");
        return;
    }

    if(sorted) converted_csv = SortCsv(converted_csv);

    var graph_data = new google.visualization.DataTable();

    var types = {
        min: "number"
        , max: "number"
        , avg: "number"
        , sum: "number"
        , count: "number"
    };

    for(var i = 0; i < converted_csv[0].length; i++)
    {
		if(isNaN(converted_csv[1][i]))
		{
			graph_data.addColumn("string", converted_csv[0][i]);
		}
		else
		{
			graph_data.addColumn("number", converted_csv[0][i]);
		}
    }

    for(var i = 1; i < Math.min(converted_csv.length, rows_count + 1); i++) // +1 - header
        graph_data.addRow(converted_csv[i]);

    var options = {
        'title': 'title'
        , 'width': 1000
        , 'height': 600
        , 'isStacked': (normalized ? "percent" : "absolute")};

    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.ColumnChart(document.getElementById(target.substr(1)));
    chart.draw(graph_data, options);
}
