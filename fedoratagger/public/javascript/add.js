$(document).ready(function () {
    var error = function() {
        $.gritter.add({
            title: 'There was a problem with the server.',
            text: 'Sorry.',
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        });
        request_in_progress = false;
    };
    var success = function(json) {
        $.gritter.add({
            title: 'Tagging ' + json.package + ' with ' + json.tag,
            text: json.msg,
            image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        });
        $('#add_dialog').dialog('close');
        request_in_progress = false;
    };

    $("#add_box").keydown(function(e){
        if( e.keyCode == 13 ){
            request_in_progress = true;
            $.ajax({
                type: "POST",
                url: "add",
                data: $.param({
                    label: $(this).val(),
                    package: $('.center * h2').html(),
                    _csrf_token: $.getUrlVar("_csrf_token"),
                }),
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
