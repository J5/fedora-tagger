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
    </body>
</html>
