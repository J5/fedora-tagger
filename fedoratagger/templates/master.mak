<html>
    <head>
        <link href="css/text.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/960_24_col.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/slider.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/voting.css" media="screen" type="text/css" rel="stylesheet"></link>
        <title>Fedora Tagger</title>
    </head>
    <body>
% if hasattr(tmpl_context, 'hotkeys_dialog'):
		${tmpl_context.hotkeys_dialog.display() | n}
% endif
% if hasattr(tmpl_context, 'search_dialog'):
		${tmpl_context.search_dialog.display() | n}
% endif
        <div id="header">
            <div><H1><span id="logo">Fedora</span> tagger</H1></div>
% if hasattr(tmpl_context, 'user_widget'):
			${tmpl_context.user_widget.display() | n}
% endif
        </div>
        <div class="clear"></div>
		${self.body()}
        <div class="clear"></div>
    </body>
</html>
