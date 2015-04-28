<html>
    <head>
        <link href="css/text.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/960_24_col.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/slider.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/voting.css" media="screen" type="text/css" rel="stylesheet"></link>
        <title>Fedora Tagger - ${title}</title>
    </head>
    <body>
% if hasattr(g, 'hotkeys_dialog') and g.hotkeys_dialog:
		${g.hotkeys_dialog.display() | n}
% endif
% if hasattr(g, 'search_dialog') and g.search_dialog:
		${g.search_dialog.display() | n}
% endif
% if hasattr(g, 'add_dialog') and g.add_dialog:
		${g.add_dialog.display() | n}
% endif
% if hasattr(g, 'statistics_dialog') and g.statistics_dialog:
		${g.statistics_dialog.display() | n}
% endif
% if hasattr(g, 'leaderboard_dialog') and g.leaderboard_dialog:
		${g.leaderboard_dialog.display() | n}
% endif
        <div id="header">
            <div><H1><span id="logo">Fedora</span> tagger</H1></div>
% if hasattr(g, 'user_widget') and g.user_widget:
			${g.user_widget.display() | n}
% endif
        </div>
        <div class="clear"></div>
		${self.body()}
        <div class="clear"></div>

		<div class="box-container">
			<div class="box searchbox-onpage">
				<input placeholder="Search for packages"/>
			</div>
		</div>
        <div class="clear"></div>

		<div id="footer">
			You can report bugs and file issues with Fedora Tagger on
			<a href="https://github.com/fedora-infra/fedora-tagger/issues">
			the GitHub issues tracker</a>.
		</div>

    % if 'FEDMENU_URL' in g.config:
    <script src="${g.config['FEDMENU_URL']}/js/fedmenu.js"></script>
    <script>
      fedmenu({
          'url': '${g.config["FEDMENU_DATA_URL"]}',
          'mimeType': 'application/javascript',
          'position': 'bottom-right',
          #### It would be really nice to be able to link directly to packages
          #### with fedmenu, but currently fedmenu can only be called once at
          #### the initial page setup.  Tagger is very javascript-driven, so we
          #### would need a way to update fedmenu with the new package icon every
          #### time the user navigates to the next tagger card.  Put this on the
          #### TODO list, low priority.
          ## % if cards:
          ## 'package': '${cards[1].package.name}',
          ## % endif
      });
    </script>
    % endif

    </body>
</html>
