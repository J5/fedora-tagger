<div class="userinfo">
  <table>
    <tr>
      <td>
        <div class="photo-64" style="display: inline-block !important;">
          <img src="${w.avatar_link(s=64)}"></img>
        </div>
      </td>
      <td style="width:4px;"></td>
      <td>
% if w.logged_in:
        <p>Logged in (<span id="username">${str(w.formatted_name)}</span>)</p>
        <p><span id="total_votes">${str(w.total_votes)}</span> votes cast.</p>
        <p>Rank: <span id="rank">${str(w.rank)}</span></p>
        <p><a href="logout_handler">Logout</a></p>
% else:
	<p>Not logged in.</p>
	<p><a href="login">Login</a> to increase your rank.</p>
% endif

      </td>
    </tr>
  </table>
</div>
