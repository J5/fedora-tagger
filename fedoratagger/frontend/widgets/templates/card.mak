<div class="${w.css_class}">
  <div class="content">
    <div class="clear"></div>
    <div class="package_header">
      <div class="title">
        % if w.package.name:
          % if w.package.icon(w.session):
            <div class="icon"><img src="${w.package.icon(w.session)}"/></div>
          % endif
          <div>
            <h2>
	      <a href="https://apps.fedoraproject.org/packages/${w.package.name}"
	        target="_blank">
	        ${w.package.name}
	      </a>
            </h2>
          </div>
          <div class="summary">
           % if w.package.summary:
             ${w.package.summary}
           % else:
             ${w.package.xapian_summary(w.session)}
           % endif
          </div>
          <div>
          % if w.package.name:
            <div class="rating_wrapper">
              <select class="rating">
                  % for i in range(6):
                  <option value="${i}"${w.rating_selected(i, 6)}></option>
                  % endfor
              </select>
            </div>
          % endif
          </div>
          % if w.not_anonymous:
            <div class="usage">
              <a href="javascript:toggle_usage('${w.package.name}');">
                <span id='count'>${w.package.usage}</span>
                <span id='count_suffix'>
                  % if w.package.usage == 1:
                    person uses this
                  % else:
                    people use this
                  % endif
                </span>
                % if w.including_you:
                  <span id='furthermore'>(including you)</span>
                % endif
              </a>
            </div>
          % endif
          <div class="clear"></div>
          % if w.package.name:
            <div class="details">
              <a href="javascript:more_details('${w.package.name}');">More details...</a>
            </div>
          % endif
        % endif
        <div class="clear"></div>
      </div>
      <div class="clear"></div>
      <div class="question">
        % if w.package.name:
          % if w.tags:
            Do these tags match this package?
          % elif not w.not_anonymous:
            This package currently has no tags.<br/>Login to help us add some:
            <button onclick="javascript:login();">Login</button>
          % endif
        % else:
          No package found.
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
</div>
