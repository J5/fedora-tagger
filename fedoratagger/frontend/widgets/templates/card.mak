<div class="${w.css_class}">
  <div class="content">
    <div class="clear"></div>
    <div class="package_header">
      <div class="title">
        % if w.package.icon:
          <div class="icon"><img src="${w.package.icon}"/></div>
        % endif
        <div><h2>${w.package.name}</h2></div>
        <div class="summary">
          % if w.package.summary:
            ${w.package.summary}
          % else:
            ${w.package.xapian_summary}
          % endif
        </div>
        <div class="rating_wrapper">
            <select class="rating">
                % for i in range(6):
                <option value="${i}"${w.rating_selected(i, 6)}></option>
                % endfor
            </select>
        </div>
      </div>
        % if w.not_anonymous:
        <div class="usage">
            <a href="javascript:toggle_usage('${w.package.name}');">
                <span id='count'>${w.package.usage}</span> people use this
                % if w.including_you:
                <span id='furthermore'>(including you)</span>
                % endif
            </a>
        </div>
        <div class="clear"></div>
        % endif
        <div class="details">
            <a href="javascript:more_details('${w.package.name}');">More details...</a>
        </div>
        <div class="clear"></div>
    </div>
    <div class="clear"></div>
    <div class="question">
      % if w.tags:
      Do these tags match this package?
      % elif not w.not_anonymous:
      This package currently has no tags.<br/>Login to help us add some:
      <button onclick="javascript:login();">Login</button>
     % endif
    </div>
    <div class="clear"></div>
    <div class="tags">
      <ul>
% for tag in w.tags:
          ${tag.display() | n}
% endfor
      </ul>
    </div>
    <div class="clear"></div>
% if w.not_anonymous:
    <div class="new">
        <div class="plus" onclick="javascript:$('#add_dialog').dialog('open');"></div>Add a new tag.
    </div>
% endif
  </div>
</div>
