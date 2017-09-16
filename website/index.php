<?php
if(empty($_SERVER['HTTPS']) || $_SERVER['HTTPS'] == "off"){
    $redirect = 'https://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
    header('HTTP/1.1 301 Moved Permanently');
    header('Location: ' . $redirect);
    exit();
}
require("inc/settings.php");
$title = "Main";
include("inc/header.php");
session_start();
print "<br><div class='loginBox' id='loginBox'>";
include("inc/navigatorbox.php");
include("inc/frontpage.php");


include("inc/footer.php");
?>