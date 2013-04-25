<%inherit file="master.mak"/>
<%def name="title()">Login Form</%def>
<div class="body" id="gameboard" style="height: 380px; width: 720px; ">
<div class="card" style="height: 360px; width: 360px; left: -234px; "></div>
<div class="card center" style="height: 360px; width: 360px; left: 180px; ">
<div class="content">
<div id="loginform">
<form action="${tg.url('/login_handler', params=dict(came_from=came_from.encode('utf-8'), __logins=login_counter.encode('utf-8')))}" method="POST" class="loginfields">
  <h2><span>Login (<a target="_blank"
        href="https://admin.fedoraproject.org/accounts">
        FAS credentials</a>)</span></h2>
    <label for="login">Username:</label><input type="text" id="login" name="login" class="text"></input><br/>
    <label for="password">Password:</label><input type="password" id="password" name="password" class="text"></input>
    <label id="labelremember" for="loginremember">remember me</label><input type="checkbox" id="loginremember" name="remember" value="2252000"/>
    <input type="submit" id="submit" value="Login" />
</form>
</div>
</div>
</div>
<div class="card" style="height: 360px; width: 360px; left: 594px; "></div>
<div id="leftfade" style="height: 380px; top: 0px; left: 0px; width: 90px; display: inline; "></div>
<div id="rightfade" style="height: 380px; right: 0px; width: 90px; display: inline; "></div>
</div>
