<%inherit file="local:templates.master"/>
<div class="body" id="gameboard">

% for card in cards:
	${card.display() | n}
% endfor

    <div id="leftfade"></div>
    <a href="#" onClick="navigate_new_card(); return false;">
	<div id="rightfade"></div>
	</a>
</div>
