var perform_search = null;

$(document).ready(function () {
    var search_term = null;

    var error = function() {
        signal_request(false);
        if (! notifications_on) { return; }
        if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
        gritter_id = $.gritter.add({
            title: 'There was a problem with the server.',
            text: 'Sorry.',
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        });
    };

    var handle_match = function(term) {
        if (notifications_on) {
            gritter_id = $.gritter.add({
                title: term,
                text: "Loading package matching '" + term + "'.",
                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            });
        }
        $("#search_dialog input").val('');
        $("#search_dialog").dialog("close");
        navigate_new_card(term, navigate_new_card);
    };

    var success = function(json) {
        // We got some search results back from the /packages app.
        // See https://github.com/fedora-infra/fedora-tagger/issues/88
        // for a description and discussion.
        signal_request(false);

        if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
        if ( json.total_rows == 0 ) {
            if (notifications_on) {
                gritter_id = $.gritter.add({
                    title: 'No results found.',
                    text: 'No results found for "' + search_term + '".',
                    image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
            }
        } else if ( json.total_rows == 1 ) {
            term = json.rows[0].name
            // First, strip the span match crap from term
            term = $('<p>' + term + '</p>').text()
            handle_match(term);
        } else if ( json.total_rows > 1 ) {
            // First, check if any of the results are exact matches.
            // If one of them is then use that one.
            var match_found = false;
            for (var i=0; i < json.rows.length; i++) {
                term = json.rows[i].name
                term = $('<p>' + term + '</p>').text()
                if ( term == search_term ) {
                    match_found = true;
                    handle_match(term);
                    break;
                }
            }
            // But if none of them were exact matches...
            if (! match_found) {
                // then redirect the user to the search results so they can
                // choose which package they want.
                gritter_id = $.gritter.add({
                    title: 'Many results found.',
                    text: 'Many results found for "' + search_term + '".  Redirecting...',
                    image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
                window.location = "https://apps.fedoraproject.org/packages/s/" + search_term;
            }
        }
    };

    $("#search_box").keydown(function(e){
        if( e.keyCode == 13 ){
            search_term = $(this).val();
            perform_search(search_term);
        }
    });

    $(".searchbox-onpage > input").keydown(function(e) {
        if( e.keyCode == 13 ){
            search_term = $(this).val();
            perform_search(search_term);
        }
    });

    perform_search = function(term) {
        signal_request(true);

        // * Construct a query against the Fedora Packages API *
        // Note that if you are running this on your own machine in dev
        // mode, that this constitutes a cross-domain XHR request which
        // will fail.  You can disable web security on your browser to hack
        // on it.
        base_url = "https://apps.fedoraproject.org/packages/fcomm_connector";
        path = "/xapian/query/search_packages/";
        query = JSON.stringify({
            filters: { search: term },
            rows_per_page: 10,
            start_row: 0,
        });
        search_url = base_url + path + query ;

        // Now make that query.
        $.ajax({
            type: "GET",
            url: search_url,
            dataType: "json",
            cache: false,
            error: error,
            success: success,
        });
    }

    $("#search_dialog").bind("dialogclose", function (e, ui) {
        $("#search_box").val('');
        $("#search_box").blur();
    });
});
