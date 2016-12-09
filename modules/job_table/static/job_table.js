// http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function update_page(date_from, date_to, req_tags, opt_tags, no_tags)
{
    window.location.href = location.protocol + '//' + location.host + "/job_table/table/0"
        + "?date_from=" + date_from + "&date_to=" + date_to
        + "&req_tags=" + req_tags
        + "&opt_tags=" + opt_tags
        + "&no_tags=" + no_tags;
}

function update_current_page()
{
	var date_to = $("#date_to").datepicker('getDate') / 1000;

	if(date_to == 0)
	{
		date_to = Math.floor(Date.now() / 1000);
	}

	var date_from = $("#date_from").datepicker('getDate') / 1000;

	if(date_from == 0)
	{
		date_from = date_to - 86400 * 3;
	}

    update_page(date_from, date_to
    	, $("#date_to").datepicker('getDate') / 1000
    	, $("#req_tags").tagit("assignedTags").join(";")
        , $("#opt_tags").tagit("assignedTags").join(";")
        , $("#no_tags").tagit("assignedTags").join(";"));
}

function set_current_page()
{
	var date_from = getParameterByName("date_from");
	var date_to = getParameterByName("date_to");

	if(!!date_from)
	{
		var prased_date_from = $.datepicker.parseDate('@', date_from * 1000);
		$("#date_from").datepicker("setDate", prased_date_from);
	}
//	else
//		$("#date_from").datepicker("setDate", "-3");

	if(!!date_to)
	{
		var parsed_date_to = $.datepicker.parseDate('@', date_to * 1000);
		$("#date_to").datepicker("setDate", parsed_date_to);
	}
//	else
//		$("#date_to").datepicker("setDate", "today");


	var date_from = $("#date_from").datepicker('getDate') / 1000;
	var date_to = $("#date_to").datepicker('getDate') / 1000;

    var filters = ["req_tags", "opt_tags", "no_tags"];

    for(var j = 0; j < filters.length; j++)
    {
        var tag_holder = filters[j];
        var data = getParameterByName(tag_holder).split(";");

        for(var i = 0; i < data.length; i++)
        {
            $("#" + tag_holder).tagit("createTag", data[i], "", true);
        }
    }

    /*var params = "?t_from=" + t_from + "&t_to=" + t_to
    	+ "&req_tags=" + $("#req_tags").tagit("assignedTags").join(";")
        + "&opt_tags=" + $("#opt_tags").tagit("assignedTags").join(";")
        + "&no_tags=" + $("#no_tags").tagit("assignedTags").join(";");

    var short_link = location.protocol + '//' + location.host + "/tasks" + params;
    var long_link = location.protocol + '//' + location.host + "/tasks_ext" + params;

    $("#short_table").attr("href", short_link);
    $("#long_table").attr("href", long_link);*/
}

function InitTags()
{
    jQuery.ajax({
        dataType: "json",
        url: "/api/tag/",
        async: false,
        success: function(data) {
            var tags = [];

            for(var i = 0; i < data.length; i++)
            {
                tags.push(data[i]["label"]);
            }

            $("#req_tags").tagit({
                allowSpaces : true,
                availableTags : tags,
                showAutocompleteOnFocus : true,
                placeholderText : "All of",

                beforeTagAdded: function(event, ui) {
                    if(tags.indexOf(ui.tagLabel) == -1)
                    {
                        return false;
                    }
                },
            });

            $("#opt_tags").tagit({
                allowSpaces : true,
                availableTags : tags,
                showAutocompleteOnFocus : true,
                placeholderText : "At least one of",

                beforeTagAdded: function(event, ui) {
                    if(tags.indexOf(ui.tagLabel) == -1)
                    {
                        return false;
                    }
                },
            });

            $("#no_tags").tagit({
                allowSpaces : true,
                availableTags : tags,
                showAutocompleteOnFocus : true,
                placeholderText : "None of",

                beforeTagAdded: function(event, ui) {
                    if(tags.indexOf(ui.tagLabel) == -1)
                    {
                        return false;
                    }
                },
            });
        }
    });
}
