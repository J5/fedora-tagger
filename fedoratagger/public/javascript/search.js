$(document).ready(function () {
        var error = function() {
                $.gritter.add({
                        title: 'There was a problem with the server.',
                        text: 'Sorry.',
                        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
        };
        var success = function(json) {
                if ( json.count == 0 ) {
                        $.gritter.add({
                                title: 'No results found.',
                                text: 'No results found for "' + json.term + '".',
                                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                        });
                } else if ( json.count > 1 ) {
                        var msg = json.count + ' results found for "' + json.term + '", like:';
                        msg += '<ul>';
                        $.each(json.samples, function(key, value) {
                                msg += '<li>' + value + '</li>';
                        });
                        msg += '</ul>';

                        msg += 'Try refining your search.';
                        $.gritter.add({
                                title: json.count + ' results found.',
                                text: msg,
                                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                        });
                } else {
                        $.gritter.add({
                                title: json.term,
                                text: "Loading package matching '" + json.term + "'.",
                                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                        });
                        $("#search_dialog").dialog("close");
                        navigate_new_card(json.term, navigate_new_card);
                }

        };

        $("#search_box").keydown(function(e){
                if( e.keyCode == 13 ){
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
