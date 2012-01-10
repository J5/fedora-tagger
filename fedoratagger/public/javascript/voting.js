function upvote(id) {
    _vote(id, true);
}
function downvote(id) {
    _vote(id, false);
}
function _vote(id, like) {
    $.ajax({
        type: "POST",
        url: "vote",
        data: $.param({
            id: id,
            like: like,
            _csrf_token: $.getUrlVar("_csrf_token"),
        }),
        cache: false,
        error: function() { failed_vote(); },
        success: function(json) {client_side_mod(id, like, json);},
    });
}

function failed_vote() {
    $.gritter.add({
        title: 'There was a problem with the server.',
        text: 'Sorry.',
        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        sticky: true,
    });
}

function client_side_mod(id, like, json) {
    $("#tag-" + id + " * .total").html(json.total);

    var dir1, dir2;
    if (like) {
        dir1 = "up";
        dir2 = "down";
    } else {
        dir1 = "down";
        dir2 = "up";
    }

    $("#tag-" + id + " * .total").addClass(dir1 + "_text");
    $("#tag-" + id + " * .total").removeClass(dir2 + "_text");

    var other = $('#tag-' + id + " * ." + dir2 + "mod");
    other.addClass(dir2);
    other.removeClass(dir2 + 'mod');

    var arrow = $("#tag-" + id + " * ." + dir1);
    arrow.removeClass(dir1);
    arrow.addClass(dir1 + 'mod');

    // Update the user thumbnail widget
    $('#total_votes').html(json.user.votes);
    $('#rank').html(json.user.rank);
}
