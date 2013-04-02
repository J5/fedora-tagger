function upvote(pkgname, tag) {
    _vote(pkgname, tag, 1);
}
function downvote(pkgname, tag) {
    _vote(pkgname, tag, -1);
}
function _vote(pkgname, tag, like) {
    $.ajax({
        type: "PUT",
        url: "../api/vote/" + pkgname + "/",
        data: {
            pkgname: pkgname,
            tag: tag,
            vote: like,
            _csrf_token: $.getUrlVar("_csrf_token"),
        },
        cache: false,
        error: function(xhr, status, err) { failed_vote(xhr, status, err); },
        success: function(json) {client_side_mod(pkgname, tag, like, json);},
    });
}

function failed_vote(xhr, status, err) {
    if (! notifications_on) { return; }
    if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
    var json = JSON.parse(xhr.responseText);
    gritter_id = $.gritter.add({
        title: 'There was a problem with the server.',
        text: json.error + "\n<br/>\n" + json.error_detail.join('.  '),
        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        sticky: true,
    });
}

function client_side_mod(pkgname, tag, like, json) {
    var selector = "#tag-" + js_escape(pkgname) + "-" + js_escape(tag);
    $(selector + " * .total").html(json.tag.total);

    var dir1, dir2;
    if (like == 1) {
        dir1 = "up";
        dir2 = "down";
    } else {
        dir1 = "down";
        dir2 = "up";
    }

    $(selector + " * .total").addClass(dir1 + "_text");
    $(selector + " * .total").removeClass(dir2 + "_text");

    var other = $(selector + " * ." + dir2 + "mod");
    other.addClass(dir2);
    other.removeClass(dir2 + 'mod');

    var arrow = $(selector + " * ." + dir1);
    arrow.removeClass(dir1);
    arrow.addClass(dir1 + 'mod');

    // Update the user thumbnail widget
    $('#total_votes').html(json.user.votes);
    $('#rank').html(json.user.rank);
    if (! notifications_on) { return; }
    if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
    gritter_id = $.gritter.add({
        title: 'OK',
        text: json.messages.join('.  '),
        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        sticky: true,
    });
}
