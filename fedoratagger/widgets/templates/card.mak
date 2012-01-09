<div class="${w.css_class}">
  <div class="content">
    <div class="clear"></div>
    <div class="package_header">
      <images src="images/icons/${w.package.name}.png" class="icon"></images>
      <div class="title">
        <div><h2>${w.package.name}</h2></div>
        <div class="clear"></div>
        <div class="summary">
          ${w.package.summary}
        </div>
      </div>
      <div class="clear"></div>
        <div class="details">
		<a href="javascript:more_details('${w.package.name}');">More details...</a>
        </div>
        <div class="clear"></div>
    </div>
    <div class="clear"></div>
    <div class="question">
      Do the following tags match this package?
    </div>
    <div class="clear"></div>
    <div class="tags">
      <ul>
% for tag in w.tags:
          ${tag.display() | n}
% endfor
      </ul>
    </div>
  </div>
</div>
