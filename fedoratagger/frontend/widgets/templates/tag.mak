<li id="tag-${w.tag.package.name.replace(' ', '-') + "-" + w.tag.label.replace(' ', '-')}" class="${w.css_class}">
<a href="#">${w.tag.label}</a>
<div id="${str(w.tag.id)}" class="voter">
  <span class="arrow up${w.upcls}"></span>
  <span class="total ${w.textcls}">${str(w.tag.total)}</span>
  <span class="arrow down${w.downcls}"></span>
</div>
</li>
