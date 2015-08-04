var card_size = 0;
var min_size = 420;
var board_margin = 10;

var gritter_id;
var request_in_progress = false;
var animation_elements = null;
var waiting_cbs = [];

function signal_request(flag) {
    request_in_progress = flag
    if ( request_in_progress ) {
        $('body').css('cursor', 'wait');
        $('#nextbutton').css('cursor', 'wait');
    } else {
        $('body').css('cursor', 'default');
        $('#nextbutton').css('cursor', 'default');
    }
}

function reflow_gradients(content) {
    var lf = document.getElementById("leftfade");
    var rf = document.getElementById("rightfade");

    lf.style.height = content.clientHeight;
    lf.style.top = 0;
    lf.style.left = 0;
    lf.style.width = card_size * 0.4;

    rf.style.height = content.clientHeight;
    rf.style.right = 0;
    rf.style.width = card_size * 0.4;

    lf.style.display = "inline";
    rf.style.display = "inline";
}

function reflow_cards() {
    var cards = $('.card');

    var card_offset = new Array();

    card_offset[0] = -(card_size * 0.65);
    card_offset[1] = card_size / 2;
    card_offset[2] = (card_size * 1.65);
    card_offset[3] = (card_size * 2.8);

    cards.each( function (index, card) {
        card.style.height = card_size;
        card.style.width = card_size;
        card.style.left = card_offset[index];
    });
}

function reflow_content(content) {
    var height = window.innerHeight;
    var width = document.innerWidth;
    var usable_height = height - (content.offsetTop * 1.5);
    var board_offset = board_margin * 2;
    card_size = usable_height - board_offset;

    if (card_size < min_size) {
        card_size = min_size;
        usable_height = min_size + board_offset;
    }

    var board_width = card_size * 2
    if (width < board_width) {
        // scale size
        card_size = card_size * (width / board_width);
        board_width = width;
    }

    content.style.height = usable_height;
    content.style.width = board_width;

    reflow_cards()
    reflow_gradients(content);
}

function reflow() {
    if (animation_elements != null) {
        animation_elements.each( function (index, el) {
            $(el).stop();
            if (index == 0)
                $(el).remove();
            });
            animation_elements = null;
    }
    var content = document.getElementById("gameboard");
    reflow_content(content);
}

function animation_complete() {
    if (animation_elements != null) {
        animation_elements.each( function (index, el) {
            $(el).stop();
            if (index == 0)
                $(el).remove();
            });
            animation_elements = null;
    }

    while (waiting_cbs.length) waiting_cbs.pop()();

    reflow_cards();
}

function animate_left() {
    if (animation_elements != null)
        return;

    animation_elements = $('.card');
    offset = card_size * 1.15;
    animation_elements.animate({"left": "-=" + offset}, "slow", animation_complete);
}

function card_new(name, callback) {
    if (animation_elements != null)
        return;

    signal_request(true);
    animate_left();
    $.ajax({
        type: "GET",
        url: "card/" + name,
        cache: false,
        data: $.param({
            _csrf_token: $.getUrlVar("_csrf_token"),
        }),
        error: function() {
            signal_request(false);
            if (! notifications_on) { return; }
            if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
            gritter_id = $.gritter.add({
                title: 'There was a problem getting the next card.',
                text: 'Sorry.',
                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            });
        },
        success: function(html) {
            $('.card:last').after(html);
            $('.card:last').css('left', (card_size * 3.5) + "px");
            $('.card:last').css('top', board_margin + "px");
            reflow_cards();
            init_mouseover();

            if (callback) {
                if (animation_elements != null) {
                    waiting_cbs.push(callback);
                } else {
                    callback();
                }
            }
            signal_request(false);
        }
    });
}

function more_details(name) {
    signal_request(true);
    $.ajax({
        type: "GET",
        url: "details",
        cache: false,
        data: $.param({
            name: name,
            _csrf_token: $.getUrlVar("_csrf_token"),
        }),
        error: function() {
            signal_request(false);
            if (! notifications_on) { return; }
            if ( gritter_id != undefined ) { $.gritter.remove(gritter_id); }
            gritter_id = $.gritter.add({
                title: 'There was a problem getting the details.',
                text: 'Sorry.',
                image: 'http://fedoraproject.org/w/uploads/6/60/Hotdog.gif',
            });
        },
        success: function(html) {
            signal_request(false);
            $("body").append("<div id='details-dialog'></div>");
            $("#details-dialog").attr('title', name);
            $("#details-dialog").html(html);
            $("#details-dialog").dialog({
                autoOpen: true,
                modal: true,
                close: function() { $('#details-dialog').dialog('destroy'); },
            });
        }
    });
}

$(document).ready(function() {
    $(window).resize(function() { reflow(); });
    reflow();
});
