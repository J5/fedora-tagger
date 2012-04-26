$(document).ready(function () {
    var error = function() {
        request_in_progress = false;
        if (! notifications_on) { return; }
        if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
        gritter_id = $.gritter.add({
            title: 'There was a problem with the server.',
            text: 'Sorry.',
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        });
    };
    var success = function(json) {
        if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
        if ( json.count == 0 ) {
            if (notifications_on) {
                gritter_id = $.gritter.add({
                    title: 'No results found.',
                    text: 'No results found for "' + json.term + '".',
                    image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
            }
        } else if ( json.count > 1 ) {
            if (notifications_on) {
                var msg = json.count + ' results found for "' + json.term + '", like:';
                msg += '<ul>';
                $.each(json.samples, function(key, value) {
                    msg += '<li>' + value + '</li>';
                });
                msg += '</ul>';

                msg += 'Try refining your search.';
                gritter_id = $.gritter.add({
                    title: json.count + ' results found.',
                    text: msg,
                    image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
            }
        } else {
            if (notifications_on) {
                gritter_id = $.gritter.add({
                    title: json.term,
                    text: "Loading package matching '" + json.term + "'.",
                    image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
            }
            $("#search_dialog input").val('');
            $("#search_dialog").dialog("close");
            navigate_new_card(json.term, navigate_new_card);
        }
        request_in_progress = false;
    };

    $("#search_box").keydown(function(e){
        if( e.keyCode == 13 ){
            request_in_progress = true;
            $.ajax({
                type: "POST",
                url: "search",
                data: $.param({
                    term: $(this).val(),
                    _csrf_token: $.getUrlVar("_csrf_token"),
                }),
                cache: false,
                error: error,
                success: success,
            });
        }
    });

    $("#search_dialog").bind("dialogclose", function (e, ui) {
        $("#search_box").blur();
    });
});
