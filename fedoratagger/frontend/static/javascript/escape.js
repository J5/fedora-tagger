var special_characters = '!"#$%&\'()*+./:;<=>?@[\\]^`{|}~';

function js_escape(str) {
    return str.replace(/ /g, '-').replace(/[\s\S]/g, function(character) {
        if (special_characters.indexOf(character) > 0) {
            return "\\" + character
        }
        return character;
    });
}
