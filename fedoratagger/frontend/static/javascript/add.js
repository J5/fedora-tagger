$(document).ready(function () {
    var error = function(xhr) {
        $("#add_dialog input").val('');
        $('#add_dialog').dialog('close');
        request_in_progress = false;
        if (! notifications_on) { return; }
        if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
        var json = JSON.parse(xhr.responseText);
        gritter_id = $.gritter.add({
            title: 'There was a problem adding that tag.',
            text: json.error,
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        });
    };
    var success = function(json) {
        $("#add_dialog input").val('');
        $('#add_dialog').dialog('close');

        // Update the user thumbnail widget
        if (json.user) {
            $('#total_votes').html(json.user.votes);
            $('#rank').html(json.user.rank);
        }

        request_in_progress = false;

        if (! notifications_on) { return; }
        if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
        gritter_id = $.gritter.add({
            title: 'OK',
            text: json.messages.join('\n<br/>\n'),
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        });
    };

    $("#add_box").keydown(function(e){
        if( e.keyCode == 13 ){
            var pkgname = $('.center * h2').html();
            request_in_progress = true;
            $.ajax({
                type: "PUT",
                url: "api/tag/" + pkgname + "/",
                data: {
                    tag: $(this).val(),
                    pkgname: pkgname,
                    _csrf_token: $.getUrlVar("_csrf_token"),
                },
                cache: false,
                error: error,
                success: success,
            });
        }
    });

    $("#add_dialog").bind("dialogclose", function (e, ui) {
        $("#add_box").blur();
    });
});
