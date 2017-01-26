// http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function fill_form()
{
	var date_from = getParameterByName("date_from");
	if(!!date_from)
	{
		var parsed_date_from = $.datepicker.parseDate('@', date_from * 1000);
		$("#date_from").datepicker("setDate", parsed_date_from);
	}

	var date_to = getParameterByName("date_to");
	if(!!date_to)
	{
		var parsed_date_to = $.datepicker.parseDate('@', date_to * 1000);
		$("#date_to").datepicker("setDate", parsed_date_to);
	}

	var accounts = getParameterByName("accounts");

    $("#accounts").val(accounts);

    var filters = ["req_tags", "opt_tags", "no_tags"];

    for(var j = 0; j < filters.length; j++)
    {
        var tag_holder = filters[j];
        var data = getParameterByName(tag_holder).split(",");

        for(var i = 0; i < data.length; i++)
        {
            $("#" + tag_holder).tagit("createTag", data[i], "", true);
        }
    }
}

function init_tags()
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
                singleField: true,
				fieldName: "req_tags",

                beforeTagAdded: function(event, ui) {
                    if(tags.indexOf(ui.tagLabel) == -1)
                    {
                        return false;
                    }
                }
            });

            $("#opt_tags").tagit({
                allowSpaces : true,
                availableTags : tags,
                showAutocompleteOnFocus : true,
                placeholderText : "At least one of",
                singleField: true,
				fieldName: "opt_tags",

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
                singleField: true,
				fieldName: "no_tags",

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
