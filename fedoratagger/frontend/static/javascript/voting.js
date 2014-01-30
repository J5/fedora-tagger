function upvote(pkgname, tag) {
    _vote(pkgname, tag, 1);
}
function downvote(pkgname, tag) {
    _vote(pkgname, tag, -1);
}
function _vote(pkgname, tag, like) {
    $.ajax({
        type: "PUT",
        url: "api/v1/vote/" + pkgname + "/",
        data: {
            pkgname: pkgname,
            tag: tag,
            vote: like,
            _csrf_token: $.getUrlVar("_csrf_token"),
        },
        cache: false,
        error: function(xhr, status, err) { failed_action(xhr, status, err); },
        success: function(json) {client_side_mod(pkgname, tag, like, json);},
    });
}

function toggle_usage(pkgname) {
    $.ajax({
        type: "PUT",
        url: "api/v1/usage/" + pkgname + "/",
        data: {
            pkgname: pkgname,
            _csrf_token: $.getUrlVar("_csrf_token"),
        },
        cache: false,
        error: function(xhr, status, err) { failed_action(xhr, status, err); },
        success: successful_usage_toggle,
    });
}

function successful_usage_toggle(json) {
    if (! notifications_on) { return; }
    if (gritter_id != undefined) { $.gritter.remove(gritter_id); }

    var change = 1;
    if ( json.messages.join('').substr(0, 13) == 'You no longer') {
        change = -1;
    }
    $('.center #count').html(
        parseInt(parseInt($('.center #count').html()) + change)
    );
    $('.center #furthermore').toggle();
    gritter_id = $.gritter.add({
        title: 'OK',
        text: json.messages.join('.  '),
        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        sticky: true,
    });
}

function rate_package(pkgname, rating) {
    $.ajax({
        type: "PUT",
        url: "api/v1/rating/" + pkgname + "/",
        data: {
            pkgname: pkgname,
            rating: rating,
            _csrf_token: $.getUrlVar("_csrf_token"),
        },
        cache: false,
        error: function(xhr, status, err) { failed_action(xhr, status, err); },
        success: successful_rating,
    });
}

function successful_rating(json) {
    if (! notifications_on) { return; }
    if (gritter_id != undefined) { $.gritter.remove(gritter_id); }
    gritter_id = $.gritter.add({
        title: 'OK',
        text: json.messages.join('.  '),
        image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
        sticky: true,
    });
}

function failed_action(xhr, status, err) {
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
    $('#total_votes').html(json.user.score);
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
