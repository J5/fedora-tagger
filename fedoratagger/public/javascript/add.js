$(document).ready(function () {
        var error = function() {
                $.gritter.add({
                        title: 'There was a problem with the server.',
                        text: 'Sorry.',
                        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
        };
        var success = function(json) {
                $.gritter.add({
                        title: 'Tagging ' + json.package + ' with ' + json.tag,
                        text: json.msg,
                        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
                });
                $('#add_dialog').dialog('close');
        };

        $("#add_box").keydown(function(e){
                if( e.keyCode == 13 ){
                        $.ajax({
                                type: "POST",
                                url: "/add",
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
                // TODO -- do something here to give key focus back to the main
                // window.  Not sure how to make it happen.
        });
});
