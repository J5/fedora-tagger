var card_size = 0;
var min_size = 360;
var board_margin = 10;

var animation_elements = null;

function reflow_gradients(content) {
    var lf = document.getElementById("leftfade");
    var rf = document.getElementById("rightfade");

    lf.style.height = content.clientHeight;
    lf.style.top = 0;
    lf.style.left = 0;
    lf.style.width = card_size * 0.25;

    rf.style.height = content.clientHeight;
    rf.style.right = 0;
    rf.style.width = card_size * 0.25;

    lf.style.display = "inline";
    rf.style.display = "inline";
}

function reflow_cards() {
    var cards = $('.card');

    var card_offset = new Array();

    card_offset[0] = -(card_size * 0.65);
    card_offset[1] = card_size / 2;
    card_offset[2] = (card_size * 1.65);

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

    reflow_cards();
}

function animate_left() {
    if (animation_elements != null)
        return;

    animation_elements = $('.card');
    offset = card_size * 1.15;
    animation_elements.animate({"left": "-=" + offset}, "slow", animation_complete);
}

function card_new() {
    if (animation_elements != null)
        return;

    // just copy the left most card for now
    var left_card = $(".card:first");
    var card_copy = left_card.clone();
    card_copy.insertAfter(".card:last");
    var card_el = card_copy.get(0)
    card_el.style.top = board_margin + "px";
    card_el.style.left = (card_size * 2.80) + "px";
}

$(document).ready(function() {
        $(document).keydown(function(e){
            if (e.keyCode == 39) {
                card_new(); animate_left();
            }
        });
        $(window).resize(function() { reflow(); });
        reflow();
});
