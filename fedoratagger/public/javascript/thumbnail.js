$(document).ready(function () {
    function error() {
        if (! notifications_on) { return; }
        if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
        gritter_id = $.gritter.add({
            title: 'There was a problem with the server.',
            text: 'Sorry.',
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            sticky: true,
        });
    }
    function success(json) {
        // Modify global variable
        notifications_on = json['notifications_on']
        if (! notifications_on) { return; }
        if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
        gritter_id = $.gritter.add({
            title: 'Notifications.',
            text: 'Notifications settings updated.',
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            sticky: true,
        });
    }
    $('#notifs_toggle').change(function () {
        $.ajax({
            type: "POST",
            url: "notifs_toggle",
            data: $.param({
                _csrf_token: $.getUrlVar("_csrf_token"),
            }),
            cache: false,
            error: error,
            success: success,
        });
    });
});
