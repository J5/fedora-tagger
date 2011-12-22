function next_item() {
        var sel = $('.center .selected');
        if (sel.next().length != 0) {
                change_selected(sel, sel.next());
        } else {
                navigate_new_card();
        }
}

function navigate_new_card(name, callback) {
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
        var center = $('.center');
        center.removeClass('center');
        center.next().addClass('center');
}

function init_mouseover() {
        $('.tags a').mouseover(function(e) {
                change_selected($('.center .selected'), $(this).parent());
        });
}

function help() { $('#hotkeys_dialog').dialog('open'); }
function search() { $("#search_dialog").dialog('open'); }

function init_navigation() {
        keys = {
                left: [37, 72],
                up: [38, 75],
                right: [39, 76],
                down: [40, 74],
                help: [27, 112],
                search: [191],
        }

        callbacks = {
                left: prev_item,
                right: next_item,
                up: upvote_this,
                down: downvote_this,
                help: help,
                search: search,
        }

        init_mouseover();

        var then = new Date();
        $(document).keyup(function(e){
                if ( $("#search_box").is(":focus") ) { return; }
                if ( animation_elements != null ) { return; }
                var now = new Date();
                if ( now - then < 250 ) { return; }
                then = now;
                for (var attr in callbacks) {
                        if ($.inArray(e.keyCode, keys[attr]) != -1) {
                                callbacks[attr]();
                        }
                }
        });
}

$(document).ready(init_navigation);
