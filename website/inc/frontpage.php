<?php
require_once("database.php");
print 'At the moment there are <b> ';
print getPlayerCount();
print '</b> accounts registered.';

if (isset($_SESSION["username"])) {
    print '<br /><br />1. Extract the ZIP.<br /><br />2. <b>Do not</b> rename the files!<br /><br />3. Play the Golden ES<br /><br />';
    print '<a href="Spurdola.zip">Download <b>here</b> and ebin blay :DDD</a>';
    //print 'Download not available right now :(';
}

?>