<li id="tag-${str(w.tag.id)}" class="${w.css_class}">
<div class="voter">
  <div class="arrow up${w.upcls}" onclick="upvote(${str(w.tag.id)});"></div>
  <div class="total ${w.textcls}">${str(w.tag.total)}</div>
  <div class="arrow down${w.downcls}" onclick="downvote(${str(w.tag.id)});"></div>
</div>
<a href="#">${w.tag.label.label}</a>
</li>
