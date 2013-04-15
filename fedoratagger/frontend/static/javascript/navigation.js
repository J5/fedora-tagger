function logout() {
    window.location = "logout_handler?" + $.param({
        came_from: window.location.href.split('?')[0]
    })
}
function login() {
    window.location = "login?" + $.param({
        came_from: window.location.href.split('?')[0]
    })
}
function next_item() {
    var sel = $('.center .selected');
    if (sel.next().length != 0) {
        change_selected(sel, sel.next());
    } else {
        navigate_new_card();
    }
}

function navigate_new_card(name, callback) {
    if ( animation_elements != null )
        return;

    var sel = $('.center .selected');
    change_card();
    change_selected(sel, $('.center li:first'));
    card_new(name, callback);
}

function prev_item() {
    var sel = $('.center .selected');
    if (sel.prev().length != 0) {
        change_selected(sel, sel.prev());
    } else {
        change_selected(sel, $('.center li:last'));
    }
}

function upvote_this() {   $('.center .selected .voter .up').click()   }

function downvote_this() { $('.center .selected .voter .down').click() }

function change_selected(from, to) {
    from.removeClass('selected');
    to.addClass('selected');
}

function change_card() {
    // Completely remove the rating widget from the center card.
    $('.center .rating_control').remove()

    // Remove clickability from tags on the center card
    $('.center .voter').children().removeAttr('onclick')

    // Remove the center class from the center card
    var center = $('.center');
    center.removeClass('center');
    center.next().addClass('center');

    var pkgname = $(".center h2").text();

    // Add the vote callbacks to the tags on the new center card.
    $('.center .voter [class*=up]').click(function() {
        var tagname = $(this).parent().parent().children('a').text();
        upvote(pkgname, tagname);
    });
    $('.center .voter [class*=down]').click(function() {
        var tagname = $(this).parent().parent().children('a').text();
        downvote(pkgname, tagname);
    });

    // Enable the rating widget
    $('.center .rating').rating({showCancel: false, callback: function(v) {
        var pkgname = $('.center .title h2').text();
        rate_package(pkgname, Math.floor((v / 5) * 100));
    }});

    // Change the window location for deep-linkage
    // Thanks to J5 for pointing out HTML5 .pushState
    var href = window.location.href;
    var val = $('.center h2').html();
    var query_string;
    if (href.indexOf('?') == -1) {
        query_string = '';
    } else {
        query_string = href.slice(href.indexOf('?'));
    }
    window.history.pushState({}, "", val + query_string);
}

function init_mouseover() {
    $('.tags li').mouseover(function(e) {
        change_selected($('.center .selected'), $(this));
    });
}

var help_opened = false;
function help() {
    if ( ! help_opened ) { $('#hotkeys_dialog').dialog('open'); }
    help_opened = ! help_opened;
}

function search() { $("#search_dialog").dialog('open'); }

function add() { $("#add_dialog").dialog('open'); }

// Multiline strings in javascript are wonderful.
var statistics_template = "                                     \
<div id='statistics-dialog'>                                    \
    <table class='statistics'>                                  \
        <tr><td>Total Packages</td><td>{0}</td></tr>            \
        <tr><td>Total Unique Tags</td><td>{1}</td></tr>         \
        <tr><td>Packages Without Tags</td><td>{2}</td></tr>     \
        <tr><td>Packages With Tags</td><td>{3}</td></tr>        \
        <tr><td>Average Tags / Package</td><td>{4}</td></tr>    \
        <tr>                                                    \
            <td>Tags / Package (that have at least one tag)</td>\
            <td>{5}</td>                                        \
        </tr>                                                   \
    </table>                                                    \
</div>";

function statistics() {
    request_in_progress = true;
    $.ajax({
        type: "GET",
        url: "api/statistics/",
        cache: false,
        data: $.param({
            _csrf_token: $.getUrlVar("_csrf_token"),
        }),
        error: function() {
            request_in_progress = false;
            if (! notifications_on) { return; }
            if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
            gritter_id = $.gritter.add({
                title: 'There was a problem getting the statistics.',
                text: 'Sorry.',
                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            });
        },
        success: function(json) {
            $("body").append("<div id='statistics-dialog'></div>");
            $("#statistics-dialog").attr('title', "Statistics");
            $("#statistics-dialog").html(statistics_template.format(
                json.summary.total_packages,
                json.summary.total_unique_tags,
                json.summary.no_tags,
                json.summary.with_tags,
                json.summary.tags_per_package.toFixed(3),
                json.summary.tags_per_package_no_zeroes.toFixed(3)
            ));
            $("#statistics-dialog").dialog({
                autoOpen: true,
                modal: true,
                close: function() { $('#statistics-dialog').dialog('destroy'); },
            });
            request_in_progress = false;
        }
    });
}

function leaderboard() {
    request_in_progress = true;
    $.ajax({
        type: "GET",
        url: "leaderboard",
        cache: false,
        data: $.param({
            _csrf_token: $.getUrlVar("_csrf_token"),
        }),
        error: function() {
            request_in_progress = false;
            if (! notifications_on) { return; }
            if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
            gritter_id = $.gritter.add({
                title: 'There was a problem getting the leaderboard.',
                text: 'Sorry.',
                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            });
        },
        success: function(html) {
            $("body").append("<div id='leaderboard-dialog'></div>");
            $("#leaderboard-dialog").attr('title', "Leaderboard");
            $("#leaderboard-dialog").html(html);
            $("#leaderboard-dialog").dialog({
                autoOpen: true,
                modal: true,
                close: function() { $('#leaderboard-dialog').dialog('destroy'); },
            });
            request_in_progress = false;
        }
    });
}
function init_navigation() {
    keys = {
        left: [37, 72],
        up: [38, 75],
        right: [39, 76],
        down: [40, 74],
        add: [65, 73],
        help: [27, 112],
        leaderboard: [66],
        statistics: [84],
        search: [83],
    }

    callbacks = {
        up: prev_item,
        down: next_item,
        right: function() { upvote_this(); next_item(); },
        left: function() { downvote_this(); next_item(); },
        add: add,
        help: help,
        leaderboard: leaderboard,
        statistics: statistics,
        search: search,
    }

    init_mouseover();

    var then = new Date();
    $(document).keyup(function(e){
        if ( $("#search_box").is(":focus") ) { return; }
        if ( $("#add_box").is(":focus") ) { return; }
        if ( animation_elements != null ) { return; }
        if ( request_in_progress ) { return; }
        var now = new Date();
        if ( now - then < 50 ) { return; }
        then = now;
        for (var attr in callbacks) {
            if ($.inArray(e.keyCode, keys[attr]) != -1) {
                callbacks[attr]();
            }
        }
    });

    var pkgname = $(".center h2").text();

    // Add the vote callbacks to the tags on the new center card.
    $('.center .voter [class*=up]').click(function() {
        var tagname = $(this).parent().parent().children('a').text();
        upvote(pkgname, tagname);
    });
    $('.center .voter [class*=down]').click(function() {
        var tagname = $(this).parent().parent().children('a').text();
        downvote(pkgname, tagname);
    });

    // Enable the rating widget
    $('.center .rating').rating({showCancel: false, callback: function(v) {
        var pkgname = $('.center .title h2').text();
        rate_package(pkgname, Math.floor((v / 5) * 99) + 1);
    }});
}

$(document).ready(init_navigation);
