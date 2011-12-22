<html>
    <head>
        <link href="css/text.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/960_24_col.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/slider.css" media="screen" type="text/css" rel="stylesheet"></link>
        <link href="css/voting.css" media="screen" type="text/css" rel="stylesheet"></link>

		<script src="javascript/cards.js" type="text/javascript"></script>
		<script src="javascript/navigation.js" type="text/javascript"></script>
        <title>Tile test</title>
    </head>
    <body>
		${tmpl_context.hotkeys_dialog.display() | n}
		${tmpl_context.search_dialog.display() | n}
        <div id="header">
            <div><H1><span id="logo">Fedora</span> tagger</H1></div>
            <div class="userinfo">Tuxytux</div>
        </div>
        <div class="clear"></div>
		${self.body()}
        <div class="clear"></div>
    </body>
</html>
