<?php
session_start();
if (!isset($_SESSION["username"])) {
    print "<p class='infotextBox'>Welcome to ".$settings['domain'].", <b>Guest</b>! </p>";
    print '<input type="button" class="toLogin" value="Login"><br><p class="infotextBox">
Not yet a member? </p><input type="button" class="toRegister" value="Register!">';
    print '</div>';
}
else {
  print '<p class="infotextBox">Welcome to '.$settings["domain"].', <b>'.$_SESSION["username"].'</b>! </p>';
  print '
  <input type="button" class="toProfile" value="My profile (TODO)"><input type="button" class="toLogout" value="Logout">';
  print '</div>';
}
?>