<%inherit file="local:templates.master"/>
<div class="body" id="gameboard">
    <div class="card">
      <div class="content">
        <div class="clear"></div>
        <div class="package_header">
          <images src="images/gvim.png" class="icon"></images>
          <div class="title">
            <div><h2>Vim</h2></div>
            <div class="clear"></div>
            <div class="summary">
              The VIM editor
            </div>
          </div>
          <div class="clear"></div>
            <div class="details">
              <a href="#">More details...</a>
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
            <li class="selected"><a href="#">keybindings</a></li>
            <li><a href="#">editor</a></li>
            <li><a href="#">operating system</a></li>
            <li><a href="#">text</a></li>
            <li><a href="#">ide</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="content">
        <div class="clear"></div>
        <div class="package_header">
          <images src="images/file-manager.png" class="icon"></images>
          <div class="title">
            <div><h2>Nautilus</h2></div>
            <div class="clear"></div>
            <div class="summary">
              A filemanager for GNOME
            </div>
          </div>
          <div class="clear"></div>
            <div class="details">
              <a href="#">More details...</a>
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
            <li class="selected"><a href="#">file-management</a></li>
            <li><a href="#">filesystem</a></li>
            <li><a href="#">browse</a></li>
            <li><a href="#">bananas</a></li>
            <li><a href="#">heimlich</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="content">
        <div class="clear"></div>
        <div class="package_header">
          <images src="images/gimp.png" class="icon"></images>
          <div class="title">
            <div><h2>Gimp</h2></div>
            <div class="clear"></div>
            <div class="summary">
              GNU Image Manipulation Program 
            </div>
          </div>
          <div class="clear"></div>
            <div class="details">
              <a href="#">More details...</a>
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
            <li class="selected"><a href="#">gegl</a></li>
            <li><a href="#">photo editor</a></li>
            <li><a href="#">bonobo</a></li>
            <li><a href="#">monkeys</a></li>
            <li><a href="#">image editor</a></li>
          </ul>
        </div>
      </div>
    </div>
    <div id="leftfade"></div>
    <a href="#" onClick="card_new(); animate_left(); return false;"><div id="rightfade"></div></a>
</div>
