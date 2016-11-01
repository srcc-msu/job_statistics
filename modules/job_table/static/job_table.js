// http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function update_page(req_tags, opt_tags, no_tags)
{
    window.location.href = location.protocol + '//' + location.host + location.pathname
        + "?req_tags=" + req_tags
        + "&opt_tags=" + opt_tags
        + "&no_tags=" + no_tags;
}

function update_current_page()
{
    update_page($("#req_tags").tagit("assignedTags").join(";")
        , $("#opt_tags").tagit("assignedTags").join(";")
        , $("#no_tags").tagit("assignedTags").join(";"));
}

function set_current_page()
{
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

    var params = "?req_tags=" + $("#req_tags").tagit("assignedTags").join(";")
        + "&opt_tags=" + $("#opt_tags").tagit("assignedTags").join(";")
        + "&no_tags=" + $("#no_tags").tagit("assignedTags").join(";");

    var short_link = location.protocol + '//' + location.host + "/tasks" + params;
    var long_link = location.protocol + '//' + location.host + "/tasks_ext" + params;

    $("#short_table").attr("href", short_link);
    $("#long_table").attr("href", long_link);
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
