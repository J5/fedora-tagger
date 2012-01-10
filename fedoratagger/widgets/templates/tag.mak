<li id="tag-${str(w.tag.id)}" class="${w.css_class}">
<a href="#">${w.tag.label.label}</a>
<div id="${str(w.tag.id)}" class="voter">
  <span class="arrow up${w.upcls}"></span>
  <span class="total ${w.textcls}">${str(w.tag.total)}</span>
  <span class="arrow down${w.downcls}"></span>
</div>
</li>
