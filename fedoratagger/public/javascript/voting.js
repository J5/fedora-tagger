function upvote(id) {
        _vote(id, "True");
}
function downvote(id) {
        _vote(id, "False");
}
function _vote(id, like) {
        $.ajax({
                type: "POST",
                url: "/vote",
                data: "id=" + id + "&like=" + like,
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

function client_side_mod(id, score, json) {
        $("#tag-" + id + " * .total").html(json.total);
}
