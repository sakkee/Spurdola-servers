<?php
global $db;
require_once("settings.php");
try {
  $db = new PDO('mysql:hostname='.$settings["dbhost"].';dbname='.$settings["dbname"], $settings["dbuser"], $settings["dbpass"]);
  $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  
  
} catch (PDOException $e) {
  echo '<div class="error">'.$e->getMessage().'</div>';
  exit;
}
function getPlayerCount() {
  global $db;
  $stmt = $db->prepare("SELECT COUNT(*) as total FROM www_accounts");
  $stmt->execute();
  $row = $stmt->fetch(PDO::FETCH_ASSOC);
  return $row['total'];
}
?>