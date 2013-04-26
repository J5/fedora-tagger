<div class="userinfo">
  <table>
    <tr>
      <td>
        <div class="photo-64" style="display: inline-block !important;">
          ${w.gravatar_tag|n}
        </div>
      </td>
      <td style="width:4px;"></td>
      <td>
% if w.logged_in:
        <p>Logged in (<span id="username">${str(w.formatted_name)}</span>)</p>
        <p><span id="total_votes">${str(w.total_votes)}</span> votes cast.</p>
        <p>Rank: <span id="rank">${str(w.rank)}</span></p>
        <p><input type="checkbox" id="notifs_toggle"
          ${str(w.notifications_on)|n} />Notifications</p>
        <p><a href="logout/">Logout</a></p>
% else:
        <form id="login_form" action="login/" method="post">
          <input type="submit" value="Login" />
        </form>
% endif
      </td>
    </tr>
  </table>
  <script type="text/javascript">
  // Global var.
  notifications_on = ${str(w._notifications_on)};
  </script>
</div>
