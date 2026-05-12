<?php
require_once "libs/paloSantoDB.class.php";
require_once "libs/paloSantoConfig.class.php";
$dsnAsterisk = "mysql://asterisk:asterisk@localhost/asterisk";
$dbAsterisk = new paloDB($dsnAsterisk);
print_r($dbAsterisk->fetchTable("SELECT id, password FROM ps_auths WHERE id LIKE '%1005%'", TRUE));
