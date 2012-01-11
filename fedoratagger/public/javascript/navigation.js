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
    // Remove clickability from tags on the center card
    $('.center .voter').children().removeAttr('onclick')

    // Remove the center class from the center card
    var center = $('.center');
    center.removeClass('center');
    center.next().addClass('center');

    // Add the vote callbacks to the tags on the new center card.
    $('.center .voter .up').click(function() {
        upvote($(this).parent().attr('id'));
    });
    $('.center .voter .down').click(function() {
        downvote($(this).parent().attr('id'));
    });
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

function leaderboard() {
    $.ajax({
        type: "POST",
        url: "leaderboard",
        cache: false,
        data: $.param({
            _csrf_token: $.getUrlVar("_csrf_token"),
        }),
        error: function() {
            $.gritter.add({
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
        search: [191],
    }

    callbacks = {
        left: prev_item,
        right: next_item,
        up: function() { upvote_this(); next_item(); },
        down: function() { downvote_this(); next_item(); },
        add: add,
        help: help,
        leaderboard: leaderboard,
        search: search,
    }

    init_mouseover();

    var then = new Date();
    $(document).keyup(function(e){
        if ( $("#search_box").is(":focus") ) { return; }
        if ( $("#add_box").is(":focus") ) { return; }
        if ( animation_elements != null ) { return; }
        var now = new Date();
        if ( now - then < 50 ) { return; }
        then = now;
        for (var attr in callbacks) {
            if ($.inArray(e.keyCode, keys[attr]) != -1) {
                callbacks[attr]();
            }
        }
    });
    navigate_new_card();
}

$(document).ready(init_navigation);
