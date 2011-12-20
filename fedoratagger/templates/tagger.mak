<%inherit file="local:templates.master"/>
<div class="body" id="gameboard">

% for card in cards:
	${card.display() | n}
% endfor

    <div id="leftfade"></div>
    <a href="#" onClick="card_new(); animate_left(); return false;">
	<div id="rightfade"></div>
	</a>
</div>
